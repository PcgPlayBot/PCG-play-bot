from PyQt6.QtWebEngineCore import QWebEnginePage


class WebPageDebugger(QWebEnginePage):
    """

    A class used to debug WebPages.
    Use this we you need to read web page js console.
    """

    def __init__(self, profile=None, debug_active=False):

        super().__init__(profile)

        self.is_debug_active = debug_active

    def javaScriptConsoleMessage(self, level, message_str, line_number, source_id):
        """Overrides default function to print js console message. We will not print Babel warning"""

        if self.is_debug_active:
            if not message_str.startswith("You are using the in-browser Babel transformer."):
                print("Message from js debug:", message_str)
