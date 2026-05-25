"""Dark theme stylesheet for PhoneHub."""

DARK_THEME = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #333355;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 8px 8px 8px;
    font-weight: bold;
    font-size: 12px;
    color: #8888cc;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QPushButton {
    background-color: #16213e;
    border: 1px solid #333355;
    border-radius: 6px;
    padding: 10px 14px;
    color: #e0e0e0;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #1f3460;
    border-color: #4a6fa5;
}

QPushButton:pressed {
    background-color: #0f1a30;
}

QPushButton:disabled {
    background-color: #0d0d1a;
    color: #555;
    border-color: #222;
}

QPushButton#danger {
    border-color: #8b0000;
    color: #ff6b6b;
}

QPushButton#danger:hover {
    background-color: #3d0000;
    border-color: #cc0000;
}

QPushButton#success {
    border-color: #006400;
    color: #6bff6b;
}

QPushButton#success:hover {
    background-color: #003d00;
    border-color: #00cc00;
}

QPushButton#accent {
    border-color: #4a6fa5;
    color: #88aaff;
}

QPushButton#accent:hover {
    background-color: #1a3a5c;
}

QLabel#status {
    color: #888;
    font-size: 12px;
    padding: 4px 8px;
}

QLabel#title {
    font-size: 18px;
    font-weight: bold;
    color: #8888cc;
}

QLabel#device-info {
    font-size: 12px;
    color: #aaa;
    padding: 2px 8px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background: #1a1a2e;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #333355;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #4a6fa5;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QLineEdit {
    background-color: #16213e;
    border: 1px solid #333355;
    border-radius: 4px;
    padding: 6px 8px;
    color: #e0e0e0;
}

QLineEdit:focus {
    border-color: #4a6fa5;
}

QProgressBar {
    background-color: #16213e;
    border: 1px solid #333355;
    border-radius: 4px;
    text-align: center;
    color: #e0e0e0;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #4a6fa5;
    border-radius: 3px;
}

QListWidget {
    background-color: #16213e;
    border: 1px solid #333355;
    border-radius: 6px;
    padding: 4px;
}

QListWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #1f3460;
}

QListWidget::item:hover {
    background-color: #1a2a4a;
}

QDialog {
    background-color: #1a1a2e;
}

QTextEdit {
    background-color: #0d0d1a;
    border: 1px solid #333355;
    border-radius: 6px;
    padding: 8px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    color: #a0ffa0;
}
"""
