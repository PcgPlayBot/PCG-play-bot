from PyQt6.QtCore import QTimer, QObject, pyqtSignal


class Worker(QObject):
    """

    This is a custom worker to execute at set interval in milliseconds.
    It looks like javascript setInterval function.
    """

    signal = pyqtSignal()

    def __init__(self, interval):
        super().__init__()

        self.interval = interval

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.signal.emit)

        self._is_working = False

    def start_timer(self):
        """Starts worker"""
        self.timer.stop()
        self.timer.start(self.interval)
        self._is_working = True

    def stop_timer(self):
        """Stops worker"""

        self.timer.stop()
        self._is_working = False

    @property
    def is_working(self):
        return self._is_working
