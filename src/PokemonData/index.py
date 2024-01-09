import re
from datetime import datetime
from threading import Thread

import requests
from dateutil import parser, tz

from assets.const.urls import POKEMON_EXTENSION_URL, POKEMON_SPAWN_URL


class PokemonData:
    """

    This class is responsible to deal with user's pokemon game data.
    It will fetch useful user data like captured pokemons, user's inventory and missions. It also should contain a
    pokedex data to handle pokemon spawns from chat.
    """

    def __init__(self, poke_data_update_callback, poke_data_error_callback):

        self._poke_jwt = None

        self._data_update_callback = poke_data_update_callback
        self._data_error_callback = poke_data_error_callback

        self._update_thread = None

        self._captured = {
            "total_count": 0,
            "unique_captured_ids": [],
            "unique_count": 0,
            "shiny_count": 0,
            "buddy_types": [],
        }

        self._inventory = {
            "cash": 0,
            "items": [],
        }

        self._missions = {
            "end_date": "",
            "missions": [],
            "target_missions": [],
        }

        self._pokedex = {
            "dex": [],
            "total_count": 0,
            "total_progress": 0,
            "spawn_count": 0,
            "spawn_progress": 0,
        }

    def update_poke_jwt(self, new_value):
        """Updates instance's pokemon API JWT to fetch requests"""

        self._poke_jwt = new_value

    def update_data(self):
        """Start thread to fetch user's pokemon data"""

        if self._poke_jwt is not None:
            self._update_thread = Thread(target=self._update_data_thread).start()

    def _update_data_thread(self):
        """Fetches user's data in a thread"""

        print("Updating pokemon data.")

        captured = handle_captured_data(self._fetch_api_data("pokemon"), self.get_pokemon_data)
        self._captured = captured if captured is not None else self.captured

        inventory = handle_inventory_data(self._fetch_api_data("inventory"))
        self._inventory = inventory if inventory is not None else self.inventory

        missions = handle_missions_data(self._fetch_api_data("mission"))
        self._missions = missions if missions is not None else self.missions

        pokedex = handle_pokedex_data(self._fetch_api_data("pokedex"))
        self._pokedex = pokedex if pokedex is not None else self.pokedex

        self._data_update_callback()

    def _fetch_api_data(self, data_type):
        """Fetches user's data from API server"""

        if self._poke_jwt is None or self._poke_jwt.exp < datetime.now():
            return None

        url = f"{POKEMON_EXTENSION_URL}/{data_type}"

        headers = {
            "Authorization": self._poke_jwt.jwt,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Pokemon data request error. Status code: {response.status_code}")
            self._data_error_callback()
            return None

    def get_pokemon_data(self, pokedex_id):
        """Fetches specific pokemon data from API server"""

        return handle_pokemon_data(self._fetch_api_data(f"pokedex/info/?pokedex_id={pokedex_id}"))

    def check_inventory(self, item_name):
        """Checks if item exists in inventory"""

        return any(item.get("sprite_name") == item_name for item in self.inventory["items"])

    @staticmethod
    def get_last_spawn_data():
        """Fetches last spawn data from API server"""

        response = requests.get(POKEMON_SPAWN_URL)

        if response.status_code == 200:
            return handle_last_spawn_data(response.json())

        else:
            print(f"Spawn data request error. Status code: {response.status_code}")
            return None

    @property
    def captured(self):
        return self._captured

    @property
    def inventory(self):
        return self._inventory

    @property
    def missions(self):
        return self._missions

    @property
    def pokedex(self):
        return self._pokedex


def handle_captured_data(server_data, get_pokemon_data):
    """Treats fetched captured pokemon data"""

    if server_data is None:
        return None

    data = {
        "total_count": len(server_data["allPokemon"]),
        "unique_captured_ids": [],
        "unique_count": 0,
        "shiny_count": 0,
        "buddy_types": [],
    }

    for pokemon in server_data["allPokemon"]:

        if pokemon["pokedexId"] not in data["unique_captured_ids"]:
            data["unique_captured_ids"].append(pokemon["pokedexId"])
            data["unique_count"] = data["unique_count"] + 1

        if pokemon["isShiny"]:
            data["shiny_count"] = data["shiny_count"] + 1

        if pokemon.get("isBuddy", False):
            buddy_data = get_pokemon_data(pokemon["pokedexId"])
            if buddy_data is not None:
                data["buddy_types"] = buddy_data["types"]

    return data


def handle_inventory_data(server_data):
    """Treats fetched inventory data"""

    if server_data is None:
        return None

    data = {
        "cash": server_data["cash"],
        "items": [
            {"name": item["name"], "amount": item["amount"], "sprite_name": item["sprite_name"]}
            for item in server_data["allItems"]
        ]
    }

    return data


# noinspection PyTypeChecker
def handle_missions_data(server_data):
    """Treats fetched missions data"""

    if server_data is None:
        return None

    data = {
        "end_date": server_data["endDate"],
        "missions": [
            {"name": item["name"], "goal": item["goal"], "progress": item["progress"]}
            for item in server_data["missions"]
        ],
        "target_missions": [],
    }

    pokemon_types = [
        "normal", "fighting", "rock", "fire", "poison", "ghost", "water", "ground", "dragon",
        "grass", "flying", "dark", "electric", "psychic", "psychic", "ice", "bug", "fairy"
    ]

    data["target_missions"] = []
    for mission in data["missions"]:

        mission_name = mission["name"].lower()

        if "catch" in mission_name and "miss" not in mission_name and mission["progress"] < mission["goal"]:

            # Tier
            if "tier" in mission_name:
                match = re.search(r"tier\s+(\w)", mission_name)
                if match:
                    data["target_missions"].append(("tier", match.group(1)))
                    continue

            # BST
            if "bst" in mission_name:
                match = re.findall(r"\d+", mission_name)
                if len(match) > 0:
                    if "greater" in mission_name or "higher" in mission_name:
                        data["target_missions"].append(("bst_greater", match[1]))
                        continue
                    elif "lower" in mission_name:
                        data["target_missions"].append(("bst_lower", match[1]))
                        continue

            # Weight
            if re.search(r"(\d+)\s*kg", mission_name):
                match = re.search(r"(\d+)\s*kg", mission_name)
                if "more than" in mission_name or "heavier" in mission_name:
                    data["target_missions"].append(("weight_greater", int(match.group(1))))
                    continue
                elif "less than" in mission_name or "lower" in mission_name:
                    data["target_missions"].append(("weight_lower", int(match.group(1))))
                    continue

            # Type count
            if "type" in mission_name and "mono" in mission_name:
                data["target_missions"].append(("type_count", 1))
                continue
            elif "type" in mission_name and "dual" in mission_name:
                data["target_missions"].append(("type_count", 2))
                continue

            # Type
            for pokemon_type in pokemon_types:
                if pokemon_type in mission_name:
                    data["target_missions"].append(("type", pokemon_type))
                    break

    return data


def handle_pokedex_data(server_data):
    """Treats fetched pokedex data"""

    if server_data is None:
        return None

    data = {
        "dex": [{"name": item["name"], "pokedex_id": item["pokedexId"]} for item in server_data["dex"]],
        "total_count": server_data["totalPkm"],
        "total_progress": server_data["progress"],
        "spawn_count": server_data["catchablePkm"],
        "spawn_progress": server_data["catchableProgress"],
    }

    return data


def handle_pokemon_data(server_data):
    """Treats fetched pokemon data"""

    if server_data is None:
        return None

    def get_pokemon_types(type1, type2):
        types = [type1, type2]
        return list(filter(lambda x: x != "none", types))

    data = {
        "pokedex_id": server_data["content"]["pokedex_id"],
        "name": server_data["content"]["name"],
        "weight": server_data["content"]["weight"],
        "types": get_pokemon_types(server_data["content"]["type1"], server_data["content"]["type2"]),
        "tier": server_data["content"]["tier"],
        "base_stats": sum(server_data["content"]["base_stats"].values()),
        "base_hp": server_data["content"]["base_stats"]["hp"],
        "base_speed": server_data["content"]["base_stats"]["speed"],
    }

    return data


def handle_last_spawn_data(server_data):
    """Treats fetched last spawn data"""

    if server_data is None:
        return None

    data = {
        "spawn_date": parser.isoparse(server_data["event_time"]).astimezone(tz.tzlocal()),
        "pokedex_id": server_data["pokedex_id"],
        "isEventSpawn": server_data["isEventSpawn"]
    }

    return data
