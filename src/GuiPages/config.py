from json import loads

from PyQt6.QtCore import QUrl, pyqtSlot, QRect
from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView

from src.TwitchLoginManager.index import WebPageDebugger
from src.helpers.SchemeHandler import QtSchemeHandler


class ConfigPage(QWebEngineView):
    """

    This is the program's configuration GUI.
    It is used to set not configurations as which balls throw and when to buy.
    """

    def __init__(self,
                 program_path,
                 on_load_callback,
                 on_save_config_callback
                 ):
        super().__init__()

        self._program_path = program_path

        self._load_callback = on_load_callback
        self._save_config_callback = on_save_config_callback

        self._channel = QWebChannel()
        self._channel.registerObject("backend_channel", self)

        self._page = WebPageDebugger(debug_active=True)
        self._page.setWebChannel(self._channel)
        self._page.loadFinished.connect(self._load_callback)

        self.setPage(self._page)

        self.setWindowTitle("Config")
        self.setWindowIcon(QIcon(f"{self._program_path}/assets/icons/gear.png"))

        self.scheme_handler = None

        self.setGeometry(QRect(0, 0, 960, 640))  # We use this because resize is exhibiting an abnormal behaviour
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        qt_rectangle = self.frameGeometry()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

    def open(self):
        """Opens the GUI page"""

        self.scheme_handler = QtSchemeHandler(self._program_path)
        self._page.profile().installUrlSchemeHandler(
            b"qt", self.scheme_handler
        )
        url = QUrl("qt://main")
        url.setPath("/config.html")
        self.load(url)

        self.show()

    def update_config_data(self, new_value):
        """Updates GUI config in page js store via qt channel"""

        self._page.runJavaScript(f"runSetConfig('{new_value}')")

    @pyqtSlot(str)
    def save_config(self, new_config):
        """Receives GUI action to save new configurations via qt channel"""

        self._save_config_callback(loads(new_config))
