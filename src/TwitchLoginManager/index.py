from json import loads

from PyQt6.QtCore import QUrl, QObject, pyqtSlot, QRect
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView

from src.helpers.WebPageDebugger import WebPageDebugger
from src.helpers.Worker import Worker

from assets.const.urls import TWITCH_POKEMON_JWT_URL, TWITCH_URL, TWITCH_OAUTH_URL


class QWebEngineWithCloseEvent(QWebEngineView):
    """

    A custom WebEngineView class.
    It uses a custom close event to clear our workers and load a blank page
    """

    def __init__(self, stop_workers):
        super().__init__()

        self._stop_workers = lambda: stop_workers()

    def closeEvent(self, event):
        self.load(QUrl("about:blank"))
        self._stop_workers()


class TwitchLoginManager(QObject):
    """

    This class is responsible to deal with Twitch login states and credentials.
    It will be used to login user on it's account and will automatically retrieve user's Pokemon API JWT and oAuth to
    login into Twitch chat via socket connection.
    """

    def __init__(self,
                 program_path,
                 twitch_connection_status_callback,
                 twitch_update_jwt_callback,
                 twitch_login_success_callback,
                 twitch_connection_timeout_callback,
                 twitch_error_callback,
                 ):

        super().__init__()

        self._program_path = program_path

        self._connection_status_callback = twitch_connection_status_callback
        self._update_jwt_callback = twitch_update_jwt_callback
        self._login_success_callback = twitch_login_success_callback
        self._connection_timeout_callback = twitch_connection_timeout_callback
        self._error_callback = twitch_error_callback

        self._injection_code = load_file_string(f"{self._program_path}/src/web/CodeInjection/TwitchInjection.js")

        self._channel = QWebChannel()
        self._channel.registerObject("backend_channel", self)

        self._web = QWebEngineWithCloseEvent(self._stop_workers)

        self._profile = QWebEngineProfile(generate_profile_id(self._program_path), self)
        self._profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)

        self._page = WebPageDebugger(self._profile, debug_active=False)
        self._page.setWebChannel(self._channel)

        self._web.setPage(self._page)
        self._web.setWindowTitle("Twitch login")

        self._web.setGeometry(QRect(0, 0, 960, 640))  # We use this because resize is exhibiting an abnormal behaviour
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        qt_rectangle = self._web.frameGeometry()
        qt_rectangle.moveCenter(center_point)
        self._web.move(qt_rectangle.topLeft())

        self._injection_worker = Worker(500)
        self._timeout_worker = Worker(15 * 1000)

        self._captured_display_name = ""

    def close_web(self):
        """Closes web engine and stop workers"""

        self._web.load(QUrl("about:blank"))
        self._web.close()
        self._stop_workers()

    def clear_cookies(self):
        """Clear cookies and close web to disconnect from Twitch"""

        self.close_web()
        self._page.profile().cookieStore().deleteAllCookies()

    def _inject_code(self, channel_code, injected_code):
        """Injects a JS code into Web page"""

        injection_code = self._injection_code
        injection_code = injection_code.replace("{channel_code}", channel_code)
        injection_code = injection_code.replace("{injected_code}", injected_code)

        self._page.runJavaScript(injection_code)

    def _start_workers(self, code_to_inject):
        """Starts workers to inject code on page and also starts time out worker"""

        channel_code = load_file_string(f"{self._program_path}/src/web/CodeInjection/QtChannel.js")

        self._injection_worker.signal.connect(lambda: self._inject_code(channel_code, code_to_inject))
        self._injection_worker.start_timer()

        self._timeout_worker.signal.connect(self._time_out_connection)
        self._timeout_worker.start_timer()

    def _stop_workers(self):
        """Stop all workers"""

        if self._timeout_worker.is_working:
            self._timeout_worker.disconnect()
            self._timeout_worker.stop_timer()

        if self._injection_worker.is_working:
            self._injection_worker.disconnect()
            self._injection_worker.stop_timer()

    def _time_out_connection(self):
        """A connection timed out. Stop everything and invokes callback"""

        print("Connection timed out!")

        self.close_web()
        self._connection_timeout_callback()

    def start_get_twitch_oauth_process(self):
        """Starts process to get Twitch oAuth. It is: check for login state and if logged go to oAuth page"""

        self._captured_display_name = ""
        self._check_login_state()

    def _check_login_state(self):
        """Checks if user is already logged in Twitch"""

        print("Checking Twitch login state.")

        self.close_web()

        injected_code = load_file_string(f"{self._program_path}/src/web/CodeInjection/TwitchLoginStateWorker.js")

        self._web.load(QUrl(TWITCH_URL))
        # self._web.show()

        self._start_workers(injected_code)

    @pyqtSlot(str)
    def login_state_callback(self, payload):
        """Callback used when a login or logout state is detected by JS code"""

        self.close_web()

        payload = loads(payload)

        if payload["isLogged"] and payload["displayName"]:
            # Proceeds to get oAuth
            self._captured_display_name = payload["displayName"]
            self._get_twitch_oauth()

        else:
            self._captured_display_name = ""
            self._connection_status_callback({
                "username": None,
                "oauth": None,
            })

    def _get_twitch_oauth(self):
        """Goes to oAuth page to retrieve oAuth code"""

        print("Getting Twitch oAuth code.")

        self.close_web()

        injected_code = load_file_string(f"{self._program_path}/src/web/CodeInjection/TwitchOauthWorker.js")

        self._web.load(QUrl(TWITCH_OAUTH_URL))
        # self._web.show()

        self._start_workers(injected_code)

    @pyqtSlot(str)
    def get_oauth_callback(self, payload):
        """Callback used when a oAuth code is detected"""

        self.close_web()

        payload = loads(payload)

        if payload["oauth"] and self._captured_display_name:
            self._connection_status_callback({
                "username": self._captured_display_name,
                "oauth": payload["oauth"],
            })

        else:
            self._captured_display_name = ""
            self._connection_status_callback({
                "username": None,
                "oauth": None,
            })

    def get_twitch_jwt(self):
        """Gets pokemon API JWT from Twitch"""

        print("Getting Twitch pokemon JWT.")

        self.close_web()

        injected_code = load_file_string(f"{self._program_path}/src/web/CodeInjection/TwitchJwtWorker.js")

        self._web.load(QUrl(TWITCH_POKEMON_JWT_URL))
        # self._web.show()

        # We must use a worker to keep injecting code because default web.startLoading is not fast enough
        self._start_workers(injected_code)

    @pyqtSlot(str)
    def get_jwt_callback(self, payload):
        """Callback used when a JWT is retrieved"""

        self.close_web()

        payload = loads(payload)

        self._update_jwt_callback(payload["jwt"])

    @pyqtSlot(str)
    def login_error(self):
        """Callback used when there is a login error"""

        self.close_web()

        self._captured_display_name = ""

        self._error_callback()

    def request_twitch_login(self):
        """Opens visible Web Page for user to login. Uses injected code to close automatically on login"""

        self.close_web()

        channel_code = load_file_string(f"{self._program_path}/src/web/CodeInjection/QtChannel.js")
        injected_code = load_file_string(f"{self._program_path}/src/web/CodeInjection/TwitchLoginWorker.js")

        self._web.load(QUrl(TWITCH_URL))

        self._web.show()

        self._injection_worker.signal.connect(lambda: self._inject_code(channel_code, injected_code))
        self._injection_worker.start_timer()

    @pyqtSlot(str)
    def login_success_callback(self, payload):
        """Callback used when a new login is detected"""

        self.close_web()

        payload = loads(payload)

        if payload["displayName"]:
            self._captured_display_name = payload["displayName"]
            self._get_twitch_oauth()
            self._login_success_callback()

        else:
            self.clear_cookies()


def generate_profile_id(unique_string):
    """Generates a unique profile Id. If it is not unique cookies will be lost"""

    from hashlib import md5

    hashed = md5(unique_string.encode()).hexdigest()
    return hashed


def load_file_string(file_path):
    """Loads injection code file as string"""

    file_string = ""

    with open(file_path, "r") as code_file:
        for line in code_file:
            file_string = file_string + line

    return file_string
