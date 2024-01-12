from datetime import datetime, timedelta
from math import floor
from random import randint
from threading import Thread
from time import sleep

from dateutil import tz

from assets.const.bot_status import BOT_STATUS


class LogicDealer:
    """

    This class is responsible to deal with our bot chat actions.
    It will define what to do when a spawn appears, which poke ball to use and when to speak on chat to keep active for
    cash earning.
    """

    def __init__(self, logic_config, pokemon_data, last_spawn_data_callback, socket_send_chat_message):

        self._logic_config = logic_config
        self._pokemon_data = pokemon_data
        self._spawn_data_callback = last_spawn_data_callback
        self._socket_send_chat_message = socket_send_chat_message

        self._handle_spawn_thread = Thread()

        self._last_spawn = None

        self._sleep_before_talking = randint(0, 30)  # We use this so we do not talk in chat always at the same time
        self._last_chat_interaction = None

    def _send_chat_message(self, command):
        """Uses socket function to send a message to chat"""

        self._last_chat_interaction = datetime.now()

        print(f"Sending chat message: '{command}'")
        self._socket_send_chat_message(command)

    def _send_catch_command(self, ball):
        """Sends the catch command with chosen ball"""

        ball_name = ball.replace("poke_ball", "").replace("_", " ")
        self._send_chat_message(f"!pokecatch {ball_name}")

    def spawn_routine(self, bot_status):
        """Main routine to be run after a spawn. It listens to new spawns, updates pokemon data and keeps chat active"""

        if self.last_spawn is None:
            self.investigate_last_spawn(bot_status)
            return

        next_spawn_date: datetime = self.last_spawn["datetime"] + timedelta(minutes=15)
        time_to_next_spawn = next_spawn_date - datetime.now(tz=tz.tzlocal())

        if time_to_next_spawn < timedelta(minutes=13, seconds=20) and not self.last_spawn["updated_data_after_spawn"]:
            self._last_spawn["updated_data_after_spawn"] = True
            self._pokemon_data.update_data()

        if time_to_next_spawn < timedelta(minutes=8, seconds=self._sleep_before_talking) \
                and not self.last_spawn["talked_in_chat_after_spawn"]:
            self._last_spawn["talked_in_chat_after_spawn"] = True
            self._handle_keep_chat_active()

        if time_to_next_spawn < timedelta(seconds=-10):
            self.investigate_last_spawn(bot_status)

    def _handle_keep_chat_active(self):
        """Keeps active in chat to receive cash"""

        if self._last_chat_interaction is None or datetime.now() - self._last_chat_interaction > timedelta(minutes=10):
            message = "$" * randint(1, 3)
            self._send_chat_message(message)

    def investigate_last_spawn(self, bot_status, chat_message=None):
        """Investigates the last spawn"""

        if not self._handle_spawn_thread.is_alive():
            self._handle_spawn_thread = Thread(target=self._investigate_last_spawn, args=(bot_status, chat_message))
            self._handle_spawn_thread.start()

    def _investigate_last_spawn(self, bot_status, chat_message):
        """Investigates the last spawn in thread. It not found on server data, fire handle from chat"""

        spawn_data = self._pokemon_data.get_last_spawn_data()

        # This is useful if we started bot just after a spawn, and pokemon data has not been loaded yet
        started_time = datetime.now()
        while len(self._pokemon_data.pokedex["dex"]) == 0 and datetime.now() - started_time < timedelta(seconds=20):
            sleep(1)

        should_capture = bot_status == BOT_STATUS["ACTIVE"]

        if spawn_data is not None and \
                (self.last_spawn is None or spawn_data["spawn_date"] != self.last_spawn["datetime"]):
            self._handle_spawn_from_server(spawn_data, should_capture)
        elif chat_message is not None and should_capture:
            self._handle_spawn_from_chat(chat_message, should_capture)

    def _handle_spawn_from_server(self, last_spawn_data, should_capture):
        """Handles spawn using data from pokemon API"""

        print("Handling spawn from server data.")

        pokemon_data = self._pokemon_data.get_pokemon_data(last_spawn_data["pokedex_id"])

        if pokemon_data is None:
            return

        self._last_spawn = {
            "pokedex_id": pokemon_data["pokedex_id"],
            "name": pokemon_data["name"],
            "datetime": last_spawn_data["spawn_date"],
            "attempt_catch": False,
            "updated_data_after_spawn": False,
            "checked_pokemon": False,
            "talked_in_chat_after_spawn": False,
        }

        spawn_data = {
            "datetime": last_spawn_data["spawn_date"],
            "is_pcg_spawn": True,
            "pokemon_data": pokemon_data,
        }

        self._spawn_data_callback({
            "name": self.last_spawn["name"],
            "datetime": self.last_spawn["datetime"].isoformat()
        })
        self._sleep_before_talking = randint(0, 30)

        if (datetime.now(tz=tz.tzlocal()) - spawn_data["datetime"]).total_seconds() < 90:
            self._handle_spawn(spawn_data, should_capture)

    def _handle_spawn_from_chat(self, chat_message, should_capture):
        """Handles spawn using message from chat"""

        print("Handling spawn from chat message.")

        id_from_message = get_pokemon_id_from_chat_message(chat_message, self._pokemon_data.pokedex["dex"])
        pokemon_data = self._pokemon_data.get_pokemon_data(id_from_message) if id_from_message is not None else None

        if pokemon_data is None:
            return

        spawn_data = {
            "datetime": datetime.now(tz=tz.tzlocal()),
            "is_pcg_spawn": False,
            "pokemon_data": pokemon_data,
        }

        self._handle_spawn(spawn_data, should_capture)

    def _handle_spawn(self, spawn_data, should_capture):
        """Handle a pokemon spawn after spawn data has been set"""

        pokemon_data = spawn_data["pokemon_data"]

        # Is it mission?
        if pokemon_data["tier"] != "S" and self._check_spawn_is_mission(pokemon_data):
            pokemon_data["tier"] = "M"

        # Is it new?
        if pokemon_data["pokedex_id"] not in self._pokemon_data.captured["unique_captured_ids"]:
            pokemon_data["tier"] = f"uncapt_{pokemon_data['tier']}"

        # Which pokeball will we use?
        chosen_ball = self._choose_capture_ball(pokemon_data) if should_capture else None

        if chosen_ball is not None:

            print(f"A wild {pokemon_data['name']} appeared! Using {chosen_ball} to attempt capture.")

            sleep_before_catch(spawn_data["datetime"], chosen_ball)

            self._send_catch_command(chosen_ball)

            if spawn_data["is_pcg_spawn"]:
                self._last_spawn["attempt_catch"] = True
            if self.last_spawn is not None:
                self._last_spawn["updated_data_after_spawn"] = False

    def _check_spawn_is_mission(self, pokemon_data):
        """Checks if a pokemon spawn is required for any mission"""

        for mission in self._pokemon_data.missions["target_missions"]:

            if mission[0] == "tier" and pokemon_data["tier"] == mission[1]:
                return True

            elif mission[0] == "bst_greater" and pokemon_data["base_stats"] > mission[1]:
                return True

            elif mission[0] == "bst_lower" and pokemon_data["base_stats"] < mission[1]:
                return True

            elif mission[0] == "weight_greater" and pokemon_data["weight"] > mission[1]:
                return True

            elif mission[0] == "weight_lower" and pokemon_data["weight"] < mission[1]:
                return True

            elif mission[0] == "type_count" and len(pokemon_data["types"]) == mission[1]:
                return True

            elif mission[0] == "type":
                for pokemon_type in pokemon_data["types"]:
                    if pokemon_type == mission[1]:
                        return True

    def _choose_capture_ball(self, pokemon_data):
        """Chooses a poke ball to attempt catch based on user's config"""

        catch_config = self._logic_config.catch[pokemon_data["tier"]]

        if "master_ball" in catch_config:
            if self._pokemon_data.check_inventory("master_ball"):
                return "master_ball"

        # elif "nest_ball" in catch_config:
        #     TODO How can we check the number of evolutions here?

        if "types_ball" in catch_config:
            for poke_type in pokemon_data["types"]:
                type_ball = get_ball_for_type(poke_type)
                if type_ball is not None and self._pokemon_data.check_inventory(type_ball):
                    return type_ball

        if "stats_ball" in catch_config:
            stat_ball = get_ball_for_stats(pokemon_data, self._logic_config.stats_balls)
            if stat_ball is not None and self._pokemon_data.check_inventory(stat_ball):
                return stat_ball

        if "timers_ball" in catch_config:
            if self._pokemon_data.check_inventory("quick_ball"):
                return "quick_ball"
            elif self._pokemon_data.check_inventory("timer_ball"):
                return "timer_ball"

        if "ultra_ball" in catch_config:
            if self._pokemon_data.check_inventory("ultra_ball"):
                return "ultra_ball"
            elif self.handle_purchase_balls("ultra_ball"):
                return "ultra_ball"

        if "friend_ball" in catch_config:
            if self._pokemon_data.check_inventory("friend_ball"):
                for poke_type in pokemon_data["types"]:
                    if poke_type in self._pokemon_data.captured["buddy_types"]:
                        return "friend_ball"

        if "repeat_ball" in catch_config:
            if "uncapt" not in pokemon_data["tier"] and self._pokemon_data.check_inventory("repeat_ball"):
                return "repeat_ball"

        if "great_ball" in catch_config:
            if self._pokemon_data.check_inventory("great_ball"):
                return "great_ball"
            elif self.handle_purchase_balls("great_ball"):
                return "great_ball"

        if "cherish_ball" in catch_config:
            if self._pokemon_data.check_inventory("ultra_cherish_ball"):
                return "ultra_cherish_ball"
            elif self._pokemon_data.check_inventory("great_cherish_ball"):
                return "great_cherish_ball"
            elif self._pokemon_data.check_inventory("cherish_ball"):
                return "cherish_ball"

        if "stone_ball" in catch_config:
            if self._pokemon_data.check_inventory("stone_ball"):
                return "stone_ball"

        if "clone_ball" in catch_config:
            if self._pokemon_data.check_inventory("clone_ball"):
                return "clone_ball"

        if "level_ball" in catch_config:
            if self._pokemon_data.check_inventory("level_ball"):
                return "level_ball"

        if "poke_ball" in catch_config:
            if self._pokemon_data.check_inventory("poke_ball") or self._pokemon_data.check_inventory("premier_ball"):
                return "poke_ball"
            elif self.handle_purchase_balls("poke_ball"):
                return "poke_ball"

        return None

    def handle_purchase_balls(self, ball):
        """Purchase balls based on user's config"""

        shop_config = self._logic_config.shop[ball]
        purchased = False

        sleep(randint(5, 10))  # We are talking too fast without this

        if not shop_config["buy_on_missing"]:
            purchased = False

        elif self._pokemon_data.inventory["cash"] > shop_config["buy_ten"]:
            self._send_chat_message(f"!pokeshop {ball.replace('_', ' ')} 10")
            purchased = True

        elif self._pokemon_data.inventory["cash"] > shop_config["buy_one"]:
            self._send_chat_message(f"!pokeshop {ball.replace('_', ' ')}")
            purchased = True

        if purchased:
            # We must sleep a little before attempting catch so we do not talk in chat too often.
            # Ideally we should not sleep more than the throw window
            sleep(60)

        return purchased

    @property
    def last_spawn(self):
        return self._last_spawn


def get_pokemon_id_from_chat_message(chat_message, pokedex):
    """"Finds out which pokemon spawned from a chat message"""

    names_matches = []
    for entry in pokedex:
        if entry["name"].lower() in chat_message.lower():
            names_matches.append(entry["pokedex_id"])

    return names_matches[-1] if len(names_matches) > 0 else None


def get_ball_for_type(poke_type):
    """Verify which typed poke ball is suited for this spawn"""

    if poke_type == "water" or poke_type == "bug":
        return "net_ball"
    elif poke_type == "ghost":
        return "phantom_ball"
    elif poke_type == "dark":
        return "night_ball"
    elif poke_type == "ice":
        return "frozen_ball"
    elif poke_type == "poison" or poke_type == "psychic":
        return "cipher_ball"
    elif poke_type == "electric" or poke_type == "steel":
        return "magnet_ball"
    else:
        return None


def get_ball_for_stats(pokemon_data, stats_balls_config):
    """Verify which stats poke ball is suited for this spawn"""

    if pokemon_data["weight"] > stats_balls_config["heavy_ball"]:
        return "heavy_ball"
    elif pokemon_data["weight"] < stats_balls_config["feather_ball"]:
        return "feather_ball"
    elif pokemon_data["base_hp"] > stats_balls_config["heal_ball"]:
        return "heal_ball"
    elif pokemon_data["base_speed"] > stats_balls_config["fast_ball"]:
        return "fast_ball"
    else:
        return None


def sleep_before_catch(spawn_date, chosen_ball):
    """"Sleeps before attempting catch. This is used to time throws and randomize bot behaviour"""

    sleep_time = 0

    if chosen_ball == "timer_ball":
        # Let's sleep till the throw time for best results
        desired_throw_time: datetime = spawn_date + timedelta(minutes=1, seconds=20)
        remaining_time = (desired_throw_time - datetime.now(tz=tz.tzlocal())).total_seconds()

        if floor(remaining_time) > 0:
            sleep_time = floor(remaining_time)

    elif chosen_ball != "quick_ball":
        # Let's sleep a random time so we look more natural
        max_wait_time: datetime = spawn_date + timedelta(minutes=1)
        remaining_time = (max_wait_time - datetime.now(tz=tz.tzlocal())).total_seconds()

        if floor(remaining_time) > 0:
            sleep_time = randint(0, floor(remaining_time))

    if sleep_time > 0:
        print(f"Sleeping {sleep_time} seconds before attempting catch.")
        sleep(sleep_time)
