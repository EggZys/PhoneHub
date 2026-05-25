"""PhoneHub — Android device control panel via scrcpy + ADB."""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from ui.styles import DARK_THEME


def main():
    # Suppress Qt logging on Windows
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_THEME)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
