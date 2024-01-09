from datetime import datetime, timedelta
from json import dumps

from PyQt6.QtWidgets import QWidget

from src.GuiPages.alert import AlertPage
from src.GuiPages.config import ConfigPage
from src.GuiPages.home import HomePage
from src.LogicConfig.index import LogicConfig
from src.LogicDealer.index import LogicDealer
from src.PokemonData.index import PokemonData
from src.TwitchLoginManager.index import TwitchLoginManager
from src.TwitchSocketManager.index import TwitchSocketManager
from src.helpers.PokeJwt import PokeJwt
from src.helpers.UserData import UserData
from src.helpers.Worker import Worker

from assets.const.bot_status import BOT_STATUS
from assets.const.connection_status import CONNECTION_STATUS


class MainApplication(QWidget):
    """

    This ou application core.
    It coordinates app actions, and connects different classes.
    """

    def __init__(self, program_path):

        super().__init__()

        self._program_path = program_path

        self._connection_status = CONNECTION_STATUS["STARTING"]
        self._bot_status = BOT_STATUS["ACTIVE"]

        self.LogicConfig = LogicConfig(
            self._program_path,
            self.update_language_callback,
            self.update_channel_callback
        )

        self.TwitchLoginManager = TwitchLoginManager(
            self._program_path,
            self.twitch_connection_status_callback,
            self.twitch_update_jwt_callback,
            self.twitch_login_success_callback,
            self.twitch_connection_timeout_callback,
            self.twitch_error_callback,
        )

        self.TwitchSocketManager = TwitchSocketManager(
            self.chat_connection_callback,
            self.chat_disconnection_callback,
            self.chat_connection_error_callback,
            self.poke_spawn_callback,
        )

        self.PokemonData = PokemonData(
            self.poke_data_update_callback,
            self.poke_data_error_callback,
        )

        self.LogicDealer = LogicDealer(
            self.LogicConfig,
            self.PokemonData,
            self.last_spawn_data_callback,
            self.TwitchSocketManager.send_chat_message
        )

        self.HomePage = HomePage(
            self._program_path,
            self.on_home_load_callback,
            self.on_home_close_callback,
            self.change_bot_status,
            self.open_config,
            self.TwitchLoginManager.request_twitch_login,
            self.twitch_logout,
        )

        self.ConfigPage = ConfigPage(
            self._program_path,
            self.on_config_load_callback,
            self.save_config_callback
        )

        self.AlertPage = AlertPage(
            self._program_path,
            self.on_alert_load_callback,
        )

        self._main_worker = Worker(1000)

        self._user_data = None
        self._poke_jwt = None

        self._time_out_error = None
        self._socket_error = None

        self.init_gui()

    def init_gui(self):
        """Initializes app home page"""

        self.HomePage.init()

    def _start_main_worker(self):
        """Starts main worker"""

        self.main_thread()

        if not self._main_worker.is_working:
            self._main_worker.signal.connect(self.main_thread)
            self._main_worker.start_timer()

    def main_thread(self):
        """Main thread that will be run by worker"""

        if self.connection_status == CONNECTION_STATUS["DISCONNECTED"] or \
                self.connection_status == CONNECTION_STATUS["ERROR"] or \
                self.bot_status == BOT_STATUS["STOPPED"]:
            return

        if self.connection_status == CONNECTION_STATUS["STARTING"]:
            self._get_twitch_oauth()

        elif self.connection_status == CONNECTION_STATUS["CONNECTED"]:

            # Refresh pokemon JWT before it expires
            if self.poke_jwt is None or self.poke_jwt.exp - datetime.now() < timedelta(minutes=10):
                print("Aqui", self.poke_jwt.exp)
                self._get_twitch_jwt()
                return

            # Keeps socket connected
            if not self.TwitchSocketManager.connected:
                self._connect_chat(self.LogicConfig.channel)
                return

            # Executes spawn routine
            self.LogicDealer.spawn_routine(self.bot_status)

        elif self.connection_status == CONNECTION_STATUS["TIMEOUT"]:
            if datetime.now() - self._time_out_error > timedelta(seconds=15):
                self._get_twitch_oauth()

        elif self.connection_status == CONNECTION_STATUS["SOCKET_ERROR"]:
            if datetime.now() - self._socket_error > timedelta(seconds=15):
                self._connect_chat(self.LogicConfig.channel)

    ### Actions ###

    def _get_twitch_oauth(self):
        """Get Twitch oAuth code to connect via chat"""

        if self.bot_status != BOT_STATUS["STOPPED"]:
            self.connection_status = CONNECTION_STATUS["LOADING"]
            self.TwitchLoginManager.start_get_twitch_oauth_process()

    def _get_twitch_jwt(self):
        """Updates Twitch JWT for pokemon API"""

        if self.bot_status != BOT_STATUS["STOPPED"]:
            self.connection_status = CONNECTION_STATUS["GETTING_JWT"]
            self.TwitchLoginManager.get_twitch_jwt()

    def _connect_chat(self, channel):
        """Creates a new socket connection to a Twitch chat"""

        if self.user_data is not None and self.bot_status != BOT_STATUS["STOPPED"]:
            self.connection_status = CONNECTION_STATUS["CONNECTING_SOCKET"]
            self.TwitchSocketManager.connect(self.user_data, channel)

    def _get_pokemon_user_data(self):
        """Updates user data from pokemon API"""

        if self.bot_status != BOT_STATUS["STOPPED"]:
            self.PokemonData.update_data()

    ### Public actions ###

    def change_bot_status(self, new_status):
        """Changes bot status"""

        if new_status == BOT_STATUS["STOPPED"]:
            self.TwitchSocketManager.disconnect()

        if self.bot_status == BOT_STATUS["STOPPED"] and new_status != BOT_STATUS["STOPPED"]:
            self.connection_status = CONNECTION_STATUS["STARTING"]
            self.main_thread()

        self.bot_status = new_status

    def open_config(self):
        """Opens config page"""

        self.ConfigPage.open()

    def twitch_logout(self):
        """Logs out from Twitch"""

        self.connection_status = CONNECTION_STATUS["DISCONNECTED"]

        self.TwitchLoginManager.clear_cookies()
        self.user_data = None
        self.poke_jwt = None

        self.TwitchSocketManager.disconnect()

        self.HomePage.reset_pokemon_data()

    ### Callbacks ###

    def update_language_callback(self, new_language):
        """Callback used when a new language config is set"""

        self.HomePage.update_language(new_language)
        self.AlertPage.update_language(new_language)

    def update_channel_callback(self, new_channel):
        """Callback used when a new channel config is set"""

        if self.connection_status == CONNECTION_STATUS["CONNECTED"]:
            self.connection_status = CONNECTION_STATUS["CONNECTING_SOCKET"]
            self.TwitchSocketManager.disconnect()
            self._connect_chat(new_channel)

        self.HomePage.update_joined_chat(new_channel)

    def twitch_connection_status_callback(self, connection_data):
        """Callback used when a Twitch login or logout state is detected"""

        # print(connection_data)

        if not connection_data["oauth"] or not connection_data["username"]:
            self.connection_status = CONNECTION_STATUS["DISCONNECTED"]
            self.user_data = None
            self.TwitchLoginManager.clear_cookies()
            self.TwitchSocketManager.disconnect()

        else:
            self.user_data = UserData(connection_data)
            self._get_twitch_jwt()

    def twitch_update_jwt_callback(self, encoded_jwt):
        """Callback used when a Twitch new pokemon API JWT data is retrieved"""

        # print(encoded_jwt)

        if self.connection_status == CONNECTION_STATUS["ERROR"]:
            return

        if not encoded_jwt:
            self.poke_jwt = None
            return

        else:
            self.poke_jwt = PokeJwt(encoded_jwt)
            self._get_pokemon_user_data()

            if self.connection_status == CONNECTION_STATUS["GETTING_JWT"]:
                if not self.TwitchSocketManager.connected:
                    self._connect_chat(self.LogicConfig.channel)
                else:
                    self.connection_status = CONNECTION_STATUS["CONNECTED"]

    def twitch_login_success_callback(self):
        """Callback used when user successfully login to Twitch"""

        self.connection_status = CONNECTION_STATUS["LOADING"]

    def twitch_connection_timeout_callback(self):
        """Callback used when an attempt to connect to Twitch times out"""

        if self.connection_status == CONNECTION_STATUS["LOADING"]:
            self.user_data = None
            self.poke_jwt = None
        elif self.connection_status == CONNECTION_STATUS["GETTING_JWT"]:
            self.poke_jwt = None

        self._time_out_error = datetime.now()
        self.connection_status = CONNECTION_STATUS["TIMEOUT"]

    def twitch_error_callback(self):
        """Callback used when an attempt to connect to Twitch returns error"""

        self.user_data = None
        self.poke_jwt = None
        self.TwitchLoginManager.clear_cookies()

        self.connection_status = CONNECTION_STATUS["ERROR"]

    def chat_connection_callback(self):
        """Callback used when a new socket connection is created"""

        if self.connection_status == CONNECTION_STATUS["CONNECTING_SOCKET"]:
            self.connection_status = CONNECTION_STATUS["CONNECTED"]

    def chat_disconnection_callback(self):
        """Callback used when a socket connection is closed. If bot is not stopped we must retry connection"""

        if self.connection_status != CONNECTION_STATUS["DISCONNECTED"] and self.bot_status != BOT_STATUS["STOPPED"]:
            self._socket_error = datetime.now()
            self.connection_status = CONNECTION_STATUS["SOCKET_ERROR"]

    def chat_connection_error_callback(self):
        """Callback used when a socket connection failed"""

        self._socket_error = datetime.now()
        self.connection_status = CONNECTION_STATUS["SOCKET_ERROR"]

    def poke_spawn_callback(self, chat_message):
        """Callback used when a pokemon spawn is detected in chat"""

        if self.bot_status != BOT_STATUS["STOPPED"]:
            self.LogicDealer.investigate_last_spawn(self.bot_status, chat_message)

    def poke_data_update_callback(self):
        """Callback used to sync GUI pokemon data with fetched from server"""

        print("Pokemon data updated.")

        if self.connection_status != CONNECTION_STATUS["DISCONNECTED"]:
            self.HomePage.update_pokemon_data(dumps({
                "captured": self.PokemonData.captured,
                "pokedex": self.PokemonData.pokedex,
                "inventory": self.PokemonData.inventory,
                "missions": self.PokemonData.missions,
            }))

    def poke_data_error_callback(self):
        """Callback when a request to pokemon API returns error. Try to reload JWT"""

        self._get_twitch_jwt()

    def last_spawn_data_callback(self, spawn_data):
        """Callback used to sync GUI last spawn data with detected from logic"""

        self.HomePage.update_last_spawn(dumps(spawn_data))

    ### GUI Callbacks ###

    def on_home_load_callback(self):
        """Callback used on home page load to update its store"""

        self.HomePage.update_connection_status(self.connection_status)
        self.HomePage.update_bot_status(self.bot_status)
        self.HomePage.update_language(self.LogicConfig.language)
        self.HomePage.update_joined_chat(self.LogicConfig.channel)
        if self.user_data is not None:
            self.HomePage.update_username(self.user_data.username)

        self._start_main_worker()

        self.AlertPage.open()

    def on_home_close_callback(self):
        """Callback used on home page close to finish app"""

        self.HomePage.close()
        self.ConfigPage.close()
        self.AlertPage.close()
        self.TwitchLoginManager.close_web()
        self.TwitchSocketManager.disconnect()

    def on_alert_load_callback(self):
        """Callback used on alert page load to update its store"""

        self.AlertPage.update_language(self.LogicConfig.language)

    def on_config_load_callback(self):
        """Callback used on config page load to update its store"""

        self.ConfigPage.update_config_data(dumps({
            "language": self.LogicConfig.language,
            "channel": self.LogicConfig.channel,
            "shop": self.LogicConfig.shop,
            "catch": self.LogicConfig.catch,
            "stats_balls": self.LogicConfig.stats_balls,
        }))

    def save_config_callback(self, new_config):
        """Callback used when user saves new settings in config page"""

        self.LogicConfig.update(new_config)
        self.on_config_load_callback()

    ### Properties ###

    @property
    def connection_status(self):
        return self._connection_status

    @connection_status.setter
    def connection_status(self, new_value):
        if self._connection_status != new_value:
            self._connection_status = new_value
            self.HomePage.update_connection_status(new_value)

    @property
    def bot_status(self):
        return self._bot_status

    @bot_status.setter
    def bot_status(self, new_value):
        if self._bot_status != new_value:
            self._bot_status = new_value
            self.HomePage.update_bot_status(new_value)

    @property
    def user_data(self):
        return self._user_data

    @user_data.setter
    def user_data(self, new_value):
        if self._user_data != new_value:
            self._user_data = new_value

            if new_value is not None:
                self.HomePage.update_username(new_value.username)

    @property
    def poke_jwt(self):
        return self._poke_jwt

    @poke_jwt.setter
    def poke_jwt(self, new_value):
        if self._poke_jwt != new_value:
            self._poke_jwt = new_value
            self.PokemonData.update_poke_jwt(new_value)
