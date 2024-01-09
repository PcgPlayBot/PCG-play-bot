import sys
from os import path

from PyQt6.QtWebEngineCore import QWebEngineUrlScheme
from PyQt6.QtWidgets import QApplication

from src.MainApplication.index import MainApplication


def except_hook(cls, exception, traceback):
    """Used to force PyQt to print exceptions"""

    sys.__excepthook__(cls, exception, traceback)


def get_program_path(main_file):
    """Gets this program folder path"""

    if getattr(sys, "frozen", False):
        application_path = path.dirname(sys.executable)

    else:
        application_path = path.abspath(path.dirname(main_file))

    return application_path


if __name__ == "__main__":

    sys.excepthook = except_hook

    scheme = QWebEngineUrlScheme(b"qt")
    QWebEngineUrlScheme.registerScheme(scheme)

    program_path = get_program_path(__file__)

    app = QApplication(sys.argv)
    core_app = MainApplication(program_path)
    sys.exit(app.exec())
