from webbrowser import open as web_open

from PyQt6.QtCore import QUrl, pyqtSlot, QRect
from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView

from src.helpers.SchemeHandler import QtSchemeHandler
from src.helpers.WebPageDebugger import WebPageDebugger


class AlertPage(QWebEngineView):
    """

    This is the program's alert page to be show on program open.
    It warns the user about using this bot and share the  GitHub page. It may also contain propaganda (◣_◢).
    """

    def __init__(self,
                 program_path,
                 on_load_callback,
                 ):
        super().__init__()

        self._program_path = program_path

        self._load_callback = on_load_callback

        self._channel = QWebChannel()
        self._channel.registerObject("backend_channel", self)

        self._page = WebPageDebugger(debug_active=True)
        self._page.setWebChannel(self._channel)
        self._page.loadFinished.connect(self._load_callback)

        self.setPage(self._page)

        self.setWindowTitle("Alert")
        self.setWindowIcon(QIcon(f"{self._program_path}/assets/icons/communist-pikachu.png"))

        self.scheme_handler = None

        self.setGeometry(QRect(0, 0, 640, 470))  # We use this because resize is exhibiting an abnormal behaviour
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
        url.setPath("/alert.html")
        self.load(url)

        self.show()

    def update_language(self, new_value):
        """Updates GUI language in page js store via qt channel"""

        self._page.runJavaScript(f"runSetLanguage('{new_value}')")

    @pyqtSlot()
    def handle_close(self):
        """Receives GUI action to close this page via qt channel"""

        self.close()

    @pyqtSlot(str)
    def handle_open_link(self, link):
        """Receives GUI action to open web link via qt channel"""

        web_open(link)
