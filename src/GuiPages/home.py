from webbrowser import open as web_open

from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSlot, QMetaObject, Qt, Q_ARG, QRect

from src.helpers.SchemeHandler import QtSchemeHandler
from src.helpers.WebPageDebugger import WebPageDebugger


class HomePage(QWebEngineView):
    """

    This is the program's config GUI.
    It is the main GUI, where we will show bot status and user's data.
    """

    def __init__(self,
                 program_path,
                 on_home_load_callback,
                 on_home_close_callback,
                 change_bot_status,
                 request_open_config,
                 request_twitch_login,
                 request_twitch_logout
                 ):
        super().__init__()

        self._program_path = program_path

        self._load_callback = on_home_load_callback
        self._close_callback = on_home_close_callback
        self._change_bot_status = change_bot_status
        self._request_open_config = request_open_config
        self._request_twitch_login = request_twitch_login
        self._request_twitch_logout = request_twitch_logout

        self._channel = QWebChannel()
        self._channel.registerObject("backend_channel", self)

        self._page = WebPageDebugger(debug_active=True)
        self._page.setWebChannel(self._channel)
        self._page.loadFinished.connect(self._load_callback)

        self.setPage(self._page)

        self.setWindowTitle("PCU Play Bot")
        self.setWindowIcon(QIcon(f"{self._program_path}/assets/icons/communist-pikachu.png"))

        self.scheme_handler = None

        self.setGeometry(QRect(0, 0, 470, 650))  # We use this because resize is exhibiting an abnormal behaviour
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        qt_rectangle = self.frameGeometry()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

    def closeEvent(self, event):
        """Close window event, we must propagate it to the main application callback"""

        self._close_callback()

    def init(self):
        """Initializes home GUI. This should be run only once"""

        self.scheme_handler = QtSchemeHandler(self._program_path)
        self._page.profile().installUrlSchemeHandler(
            b"qt", self.scheme_handler
        )
        url = QUrl("qt://main")
        url.setPath("/index.html")
        self.load(url)

        self.show()

    def update_connection_status(self, new_value):
        """Updates connection status in page js store via qt channel"""

        self._invoke_update_store(f"runSetConnectionStatus('{new_value}')")

    def update_bot_status(self, new_value):
        """Updates bot status in page js store via qt channel"""

        self._invoke_update_store(f"runSetBotStatus('{new_value}')")

    def update_language(self, new_value):
        """Updates GUI language in page js store via qt channel"""

        self._invoke_update_store(f"runSetLanguage('{new_value}')")

    def update_username(self, new_value):
        """Updates username in page js store via qt channel"""

        self._invoke_update_store(f"runSetUsername('{new_value}')")

    def update_joined_chat(self, new_value):
        """Updates joined chat in page js store via qt channel"""

        self._invoke_update_store(f"runSetJoinedChat('{new_value}')")

    def update_last_spawn(self, new_value):
        """Updates last spawn data in page js store via qt channel"""

        self._invoke_update_store(f"runSetLastSpawn('{new_value}')")

    def update_pokemon_data(self, new_value):
        """Updates users's pokemon data in page js store via qt channel"""

        self._invoke_update_store(f"runSetPokemonData(`{new_value}`)")

    def reset_pokemon_data(self):
        """Resets pokemon data in page js store via qt channel"""

        self._invoke_update_store("runResetPokemonData()")

    def _invoke_update_store(self, command):
        """Channel update store to main thread. Otherwise it throws error if update comes from a different thread"""

        QMetaObject.invokeMethod(self, '_run_page_script', Qt.ConnectionType.QueuedConnection, Q_ARG(str, command))
        
    @pyqtSlot(str)
    def _run_page_script(self, command):
        """Run script on page from main thread"""

        self._page.runJavaScript(command)

    @pyqtSlot(str)
    def change_bot_status(self, new_status):
        """Receives GUI action to change bot status via qt channel"""

        self._change_bot_status(new_status)

    @pyqtSlot()
    def request_open_config(self):
        """Receives GUI action to open config page via qt channel"""

        self._request_open_config()

    @pyqtSlot()
    def request_twitch_login(self):
        """Receives GUI action to open Twitch login page via qt channel"""

        self._request_twitch_login()

    @pyqtSlot()
    def request_twitch_logout(self):
        """Receives GUI action to disconnect Twitch account via qt channel"""

        self._request_twitch_logout()

    @pyqtSlot(str)
    def handle_open_link(self, link):
        """Receives GUI action to open web link via qt channel"""

        web_open(link)
