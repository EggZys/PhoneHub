"""Device detection and status monitoring."""

from PyQt6.QtCore import QThread, pyqtSignal

from core import adb


class DeviceWatcher(QThread):
    """Background thread that monitors device connection status."""
    connected = pyqtSignal(str)   # serial
    disconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, poll_interval: float = 2.0):
        super().__init__()
        self._running = True
        self._poll_interval = poll_interval
        self._last_serial: str | None = None

    def run(self):
        import time
        while self._running:
            try:
                devices = adb.get_devices()
                if devices and self._last_serial is None:
                    self._last_serial = devices[0]
                    self.connected.emit(devices[0])
                elif not devices and self._last_serial is not None:
                    self._last_serial = None
                    self.disconnected.emit()
            except Exception as e:
                self.error.emit(str(e))
            time.sleep(self._poll_interval)

    def stop(self):
        self._running = False
        self.wait(3000)
