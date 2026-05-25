<div align="center">

# 📱 PhoneHub

### Unified Android Control Center for Desktop

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-6.6+-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p>
  <strong>Mirror your screen. Manage your files. Control your device.</strong><br/>
  All from one beautiful dark-themed desktop interface.
</p>

<br/>

<img src="https://via.placeholder.com/900x500/1a1a2e/eee?text=PhoneHub+Screenshot" alt="PhoneHub Screenshot" width="700"/>

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🖥️ Screen Mirroring
Real-time phone screen mirroring via **scrcpy** with configurable FPS, bitrate, and display options.

### 📁 File Management
- Install **APK** and **XAPK** files
- Push files to device
- Pull files from device

### 📸 Screen Capture
- Take instant **screenshots** (PNG)
- Record screen up to **180 seconds**
- Turn screen on/off remotely

</td>
<td width="50%">

### 📦 App Manager
- Browse all installed apps
- Search & filter
- Launch or uninstall with one click

### 🔧 Device Control
- Clipboard sync (PC ↔ Phone)
- Reboot to system / recovery / bootloader
- Interactive ADB shell

### ⚡ Fastboot Support
- Detect fastboot devices
- Flash images to partitions
- Reboot between modes

</td>
</tr>
</table>

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.11 or higher |
| **scrcpy** | Installed at `C:\scrcpy\` ([Download](https://github.com/Genymobile/scrcpy)) |
| **ADB** | Bundled with scrcpy or Android SDK Platform Tools |
| **USB Debugging** | Enabled on your Android device |

### Installation

```bash
# Clone the repository
git clone https://github.com/EggZys/PhoneHub.git
cd PhoneHub

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

> **Note:** Paths to `adb.exe`, `scrcpy.exe`, and `fastboot.exe` are configured in `core/adb.py` and `core/scrcpy.py`. Update them if your tools are installed elsewhere.

---

## 🏗️ Architecture

```
PhoneHub/
├── main.py              # Entry point
├── requirements.txt     # Dependencies (PyQt6)
│
├── core/                # Backend logic
│   ├── adb.py           # ADB & Fastboot command wrappers
│   ├── scrcpy.py        # Scrcpy process manager
│   └── device.py        # Background device connection watcher
│
└── ui/                  # Frontend (PyQt6)
    ├── styles.py        # Dark theme QSS stylesheet
    ├── main_window.py   # Main window layout
    └── panels.py        # UI control panels
```

**Clean separation:** `core/` handles all subprocess/ADB interactions, `ui/` manages Qt widgets and user interaction. A `DeviceWatcher` thread bridges them via Qt signals.

---

## 🎨 Interface

The app features a **dark navy/purple theme** with carefully designed accent colors:

| Color | Usage |
|---|---|
| 🔵 Blue | Action buttons (connect, capture) |
| 🟢 Green | Success states (connected) |
| 🔴 Red | Destructive actions (uninstall, flash) |
| 🟡 Yellow | Warning states |

All long-running operations run in **background threads** — the UI never freezes.

---

## 🛠️ Tech Stack

- **Python 3.11** — Core language
- **PyQt6** — Desktop GUI framework
- **scrcpy** — Android screen mirroring engine
- **ADB** — Android Debug Bridge for device communication
- **Fastboot** — Low-level device operations

---

## 📋 Requirements

```
PyQt6>=6.6.0
```

That's it. One dependency. The app relies on external tools (scrcpy, ADB) that are installed separately.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ and Python**

<br/>

⭐ Star this repo if you find it useful!

</div>
