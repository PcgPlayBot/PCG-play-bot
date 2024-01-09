from os import path

from PyQt6.QtCore import QFile, QFileInfo, QMimeDatabase
from PyQt6.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob


class QtSchemeHandler(QWebEngineUrlSchemeHandler):
    """

    A class to open our custom GUI pages.
    Since we opted to use web engines as our gui we need this to load extra files from folder.
    """

    def __init__(self, program_path):

        super(QWebEngineUrlSchemeHandler, self).__init__()

        self._gui_path = f"{program_path}/src/web/GuiPages"

    def requestStarted(self, job):
        """Overrides default function to pass our folder to GUI"""

        request_method = job.requestMethod()

        if request_method != b"GET":
            job.fail(QWebEngineUrlRequestJob.Error.RequestDenied)
            return

        request_url = job.requestUrl()
        request_path = request_url.path()

        file_path = path.join(self._gui_path, request_path[1:])

        file = QFile(file_path)
        file.setParent(job)
        job.destroyed.connect(file.deleteLater)

        if not file.exists() or file.size() == 0:
            print(f"Resource '{request_path}' not found or is empty")
            job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)
            return

        file_info = QFileInfo(file)
        mime_database = QMimeDatabase()
        mime_type = mime_database.mimeTypeForFile(file_info)
        job.reply(mime_type.name().encode(), file)
