"""Main window layout for PhoneHub."""

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QStatusBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication

from core.scrcpy import ScrcpyManager
from core.device import DeviceWatcher
from ui.panels import LeftPanel


class MainWindow(QMainWindow):
    """PhoneHub main window — control panel on the left, scrcpy on the right."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhoneHub")
        self.setMinimumSize(340, 700)

        self._scrcpy = ScrcpyManager()
        self._init_ui()
        self._init_watcher()
        self._position_window()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._panel = LeftPanel(self._scrcpy)
        layout.addWidget(self._panel)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready — connect a device")

        # Connect panel signals
        self._panel.connection.status_message.connect(self._status_bar.showMessage)
        self._panel.connection.device_connected.connect(self._on_device_connected)
        self._panel.connection.device_disconnected.connect(self._on_device_disconnected)

    def _init_watcher(self):
        self._watcher = DeviceWatcher(poll_interval=3.0)
        self._watcher.connected.connect(self._on_auto_connected)
        self._watcher.disconnected.connect(self._on_auto_disconnected)
        self._watcher.start()

    def _position_window(self):
        """Position the window on the left half of the primary screen."""
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        # Left panel: left 300px, full height
        self.setGeometry(geo.x(), geo.y(), 320, geo.height())

    def _on_device_connected(self, serial: str):
        self._status_bar.showMessage(f"Connected: {serial}")

    def _on_device_disconnected(self):
        self._status_bar.showMessage("Device disconnected")

    def _on_auto_connected(self, serial: str):
        """Auto-detected device — update status bar only."""
        if not self._panel.connection.is_connected:
            self._status_bar.showMessage(f"Device detected: {serial} — click Connect")

    def _on_auto_disconnected(self):
        if not self._panel.connection.is_connected:
            self._status_bar.showMessage("No device connected")

    def closeEvent(self, event):
        """Clean up on close."""
        self._watcher.stop()
        self._scrcpy.stop()
        event.accept()
