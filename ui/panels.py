"""Left panel with button groups for device control."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QLabel, QLineEdit, QFileDialog, QMessageBox, QDialog,
    QListWidget, QInputDialog, QApplication, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread

from core import adb
from core.scrcpy import ScrcpyManager


class _Worker(QThread):
    """Generic background worker."""
    finished = pyqtSignal(bool, str)

    def __init__(self, fn, *args):
        super().__init__()
        self._fn = fn
        self._args = args

    def run(self):
        try:
            result = self._fn(*self._args)
            if isinstance(result, tuple):
                self.finished.emit(*result)
            else:
                self.finished.emit(True, str(result))
        except Exception as e:
            self.finished.emit(False, str(e))


class ConnectionGroup(QGroupBox):
    """Device connection controls."""
    device_connected = pyqtSignal(str)
    device_disconnected = pyqtSignal()
    status_message = pyqtSignal(str)

    def __init__(self, scrcpy: ScrcpyManager, parent=None):
        super().__init__("Connection", parent)
        self._scrcpy = scrcpy
        self._connected = False
        self._workers = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self._status_label = QLabel("No device connected")
        self._status_label.setObjectName("device-info")
        layout.addWidget(self._status_label)

        self._info_label = QLabel("")
        self._info_label.setObjectName("device-info")
        self._info_label.setWordWrap(True)
        layout.addWidget(self._info_label)

        btn_row = QHBoxLayout()

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setObjectName("success")
        self._connect_btn.clicked.connect(self._on_connect)
        btn_row.addWidget(self._connect_btn)

        self._disconnect_btn = QPushButton("Disconnect")
        self._disconnect_btn.setObjectName("danger")
        self._disconnect_btn.setEnabled(False)
        self._disconnect_btn.clicked.connect(self._on_disconnect)
        btn_row.addWidget(self._disconnect_btn)

        layout.addLayout(btn_row)

        self._refresh_btn = QPushButton("Refresh Device Info")
        self._refresh_btn.clicked.connect(self._refresh_info)
        layout.addWidget(self._refresh_btn)

    def _on_connect(self):
        self._connect_btn.setEnabled(False)
        self._connect_btn.setText("Searching...")
        w = _Worker(adb.get_devices)
        w.finished.connect(self._on_devices_found)
        self._workers.append(w)
        w.start()

    def _on_devices_found(self, ok, msg):
        self._workers = [w for w in self._workers if w.isRunning()]
        self._connect_btn.setText("Connect")
        if not ok or not msg:
            self._connect_btn.setEnabled(True)
            QMessageBox.warning(self, "No Device", "No Android device found.\nCheck USB and enable USB debugging.")
            return

        # msg here is actually the device list repr from _Worker, but get_devices returns list
        # We need to handle this differently
        devices = adb.get_devices()
        if not devices:
            self._connect_btn.setEnabled(True)
            QMessageBox.warning(self, "No Device", "No Android device found.")
            return

        self._connected = True
        serial = devices[0]
        self._connect_btn.setEnabled(False)
        self._disconnect_btn.setEnabled(True)
        self._status_label.setText(f"Connected: {serial}")
        self.device_connected.emit(serial)
        self._refresh_info()

        ok, msg = self._scrcpy.start()
        self.status_message.emit(msg)

    def _on_disconnect(self):
        self._scrcpy.stop()
        self._connected = False
        self._connect_btn.setEnabled(True)
        self._disconnect_btn.setEnabled(False)
        self._status_label.setText("Disconnected")
        self._info_label.setText("")
        self.device_disconnected.emit()
        self.status_message.emit("Disconnected")

    def _refresh_info(self):
        if not self._connected:
            return
        info = adb.get_device_info()
        battery = adb.get_battery_info()
        text = f"{info.get('model', 'N/A')}  |  Android {info.get('version', 'N/A')}"
        if battery.get("level"):
            text += f"\nBattery: {battery['level']}%  ({battery.get('status', 'N/A')})"
        self._info_label.setText(text)

    @property
    def is_connected(self) -> bool:
        return self._connected


class FileGroup(QGroupBox):
    """File operations: install APK, push/pull files."""

    def __init__(self, parent=None):
        super().__init__("Files", parent)
        self._workers = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self._apk_btn = QPushButton("Install APK / XAPK")
        self._apk_btn.setObjectName("accent")
        self._apk_btn.clicked.connect(self._install_apk)
        layout.addWidget(self._apk_btn)

        self._push_btn = QPushButton("Push File to Phone")
        self._push_btn.clicked.connect(self._push_file)
        layout.addWidget(self._push_btn)

        self._pull_btn = QPushButton("Pull File from Phone")
        self._pull_btn.clicked.connect(self._pull_file)
        layout.addWidget(self._pull_btn)

    def _install_apk(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select APK", "", "APK/XAPK Files (*.apk *.xapk)")
        if not path:
            return
        self._apk_btn.setEnabled(False)
        self._apk_btn.setText("Installing...")
        w = _Worker(adb.install_apk, path)
        w.finished.connect(self._on_install_done)
        self._workers.append(w)
        w.start()

    def _on_install_done(self, ok, msg):
        self._workers = [w for w in self._workers if w.isRunning()]
        self._apk_btn.setEnabled(True)
        self._apk_btn.setText("Install APK / XAPK")
        if ok:
            QMessageBox.information(self, "Success", "Installed successfully!")
        else:
            QMessageBox.critical(self, "Install Failed", msg)

    def _push_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File to Push")
        if not path:
            return
        self._push_btn.setEnabled(False)
        self._push_btn.setText("Pushing...")
        w = _Worker(adb.push_file, path)
        w.finished.connect(self._on_push_done)
        self._workers.append(w)
        w.start()

    def _on_push_done(self, ok, msg):
        self._workers = [w for w in self._workers if w.isRunning()]
        self._push_btn.setEnabled(True)
        self._push_btn.setText("Push File to Phone")
        if ok:
            QMessageBox.information(self, "Success", "Pushed to /sdcard/Download/")
        else:
            QMessageBox.critical(self, "Push Failed", msg)

    def _pull_file(self):
        remote, ok = QInputDialog.getText(self, "Pull File", "Remote path:", text="/sdcard/Download/")
        if not ok or not remote:
            return
        local_dir = QFileDialog.getExistingDirectory(self, "Save to...")
        if not local_dir:
            return
        self._pull_btn.setEnabled(False)
        self._pull_btn.setText("Pulling...")
        w = _Worker(adb.pull_file, remote, local_dir)
        w.finished.connect(self._on_pull_done)
        self._workers.append(w)
        w.start()

    def _on_pull_done(self, ok, msg):
        self._workers = [w for w in self._workers if w.isRunning()]
        self._pull_btn.setEnabled(True)
        self._pull_btn.setText("Pull File from Phone")
        if ok:
            QMessageBox.information(self, "Success", f"File pulled: {msg}")
        else:
            QMessageBox.critical(self, "Pull Failed", msg)


class ScreenGroup(QGroupBox):
    """Screen controls: screenshot, record, power."""

    def __init__(self, parent=None):
        super().__init__("Screen", parent)
        self._recording_proc = None
        self._workers = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self._ss_btn = QPushButton("Screenshot")
        self._ss_btn.setObjectName("accent")
        self._ss_btn.clicked.connect(self._screenshot)
        layout.addWidget(self._ss_btn)

        self._rec_btn = QPushButton("Start Recording")
        self._rec_btn.clicked.connect(self._toggle_record)
        layout.addWidget(self._rec_btn)

        self._screen_off_btn = QPushButton("Turn Off Screen")
        self._screen_off_btn.clicked.connect(lambda: adb.power_off_screen())
        layout.addWidget(self._screen_off_btn)

        self._wake_btn = QPushButton("Wake Screen")
        self._wake_btn.clicked.connect(lambda: adb.wake_screen())
        layout.addWidget(self._wake_btn)

    def _screenshot(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenshot", "screenshot.png", "PNG Files (*.png)"
        )
        if not save_path:
            return
        self._ss_btn.setEnabled(False)
        self._ss_btn.setText("Taking...")
        w = _Worker(adb.screenshot, save_path)
        w.finished.connect(lambda ok, msg: self._on_ss_done(ok, msg, save_path))
        self._workers.append(w)
        w.start()

    def _on_ss_done(self, ok, msg, path):
        self._workers = [w for w in self._workers if w.isRunning()]
        self._ss_btn.setEnabled(True)
        self._ss_btn.setText("Screenshot")
        if ok:
            QMessageBox.information(self, "Screenshot", f"Saved to:\n{path}")
        else:
            QMessageBox.critical(self, "Error", msg)

    def _toggle_record(self):
        if self._recording_proc and self._recording_proc.poll() is None:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Recording", "recording.mp4", "MP4 Files (*.mp4)"
            )
            if save_path:
                import time
                self._recording_proc.terminate()
                self._recording_proc.wait(timeout=10)
                time.sleep(2)
                ok, msg = adb.pull_file("/sdcard/phonehub_record.mp4", save_path)
                adb._run(["shell", "rm", "/sdcard/phonehub_record.mp4"])
                if ok:
                    QMessageBox.information(self, "Recording", f"Saved to:\n{save_path}")
                else:
                    QMessageBox.critical(self, "Error", msg)
            else:
                self._recording_proc.terminate()
            self._recording_proc = None
            self._rec_btn.setText("Start Recording")
        else:
            self._recording_proc = adb.screen_record_start("")
            self._rec_btn.setText("Stop Recording")


class DeviceGroup(QGroupBox):
    """Device controls: reboot, clipboard, shell."""

    def __init__(self, parent=None):
        super().__init__("Device", parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        clip_row = QHBoxLayout()
        self._clip_get_btn = QPushButton("Get Clipboard")
        self._clip_get_btn.clicked.connect(self._get_clipboard)
        clip_row.addWidget(self._clip_get_btn)

        self._clip_set_btn = QPushButton("Set Clipboard")
        self._clip_set_btn.clicked.connect(self._set_clipboard)
        clip_row.addWidget(self._clip_set_btn)
        layout.addLayout(clip_row)

        self._reboot_btn = QPushButton("Reboot")
        self._reboot_btn.clicked.connect(lambda: self._reboot(""))
        layout.addWidget(self._reboot_btn)

        reboot_row = QHBoxLayout()
        self._recovery_btn = QPushButton("Recovery")
        self._recovery_btn.clicked.connect(lambda: self._reboot("recovery"))
        reboot_row.addWidget(self._recovery_btn)

        self._bootloader_btn = QPushButton("Bootloader")
        self._bootloader_btn.setObjectName("danger")
        self._bootloader_btn.clicked.connect(lambda: self._reboot("bootloader"))
        reboot_row.addWidget(self._bootloader_btn)
        layout.addLayout(reboot_row)

        self._shell_btn = QPushButton("Open ADB Shell")
        self._shell_btn.setObjectName("accent")
        self._shell_btn.clicked.connect(self._open_shell)
        layout.addWidget(self._shell_btn)

    def _get_clipboard(self):
        text = adb.get_clipboard()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Clipboard", f"Copied to PC clipboard:\n{text[:500]}")
        else:
            QMessageBox.information(self, "Clipboard", "Device clipboard is empty")

    def _set_clipboard(self):
        text = QApplication.clipboard().text()
        if not text:
            QMessageBox.information(self, "Clipboard", "PC clipboard is empty")
            return
        ok = adb.set_clipboard(text)
        if ok:
            QMessageBox.information(self, "Clipboard", "Text set on device clipboard")
        else:
            QMessageBox.critical(self, "Error", "Failed to set device clipboard")

    def _reboot(self, mode: str):
        label = mode.title() if mode else "Reboot"
        reply = QMessageBox.question(
            self, label, f"Are you sure you want to {label.lower()} the device?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            adb.reboot(mode)

    def _open_shell(self):
        import subprocess
        try:
            subprocess.Popen(
                ["cmd", "/k", adb.get_adb_path(), "shell"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open shell:\n{e}")


class BootloaderGroup(QGroupBox):
    """Fastboot controls for bootloader mode."""

    def __init__(self, parent=None):
        super().__init__("Bootloader (Fastboot)", parent)
        self._workers = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self._status_label = QLabel("Check: reboot to bootloader first")
        self._status_label.setObjectName("device-info")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        self._check_btn = QPushButton("Detect Fastboot Device")
        self._check_btn.clicked.connect(self._check_fastboot)
        layout.addWidget(self._check_btn)

        self._reboot_sys_btn = QPushButton("Reboot to System")
        self._reboot_sys_btn.setObjectName("success")
        self._reboot_sys_btn.setEnabled(False)
        self._reboot_sys_btn.clicked.connect(self._reboot_system)
        layout.addWidget(self._reboot_sys_btn)

        self._reboot_rec_btn = QPushButton("Reboot to Recovery")
        self._reboot_rec_btn.setEnabled(False)
        self._reboot_rec_btn.clicked.connect(self._reboot_recovery)
        layout.addWidget(self._reboot_rec_btn)

        self._reboot_bl_btn = QPushButton("Reboot Bootloader")
        self._reboot_bl_btn.setEnabled(False)
        self._reboot_bl_btn.clicked.connect(self._reboot_bootloader)
        layout.addWidget(self._reboot_bl_btn)

        self._flash_btn = QPushButton("Flash Image...")
        self._flash_btn.setObjectName("accent")
        self._flash_btn.setEnabled(False)
        self._flash_btn.clicked.connect(self._flash_image)
        layout.addWidget(self._flash_btn)

    def _check_fastboot(self):
        self._check_btn.setEnabled(False)
        self._check_btn.setText("Checking...")
        w = _Worker(adb.fastboot_devices)
        w.finished.connect(self._on_check_done)
        self._workers.append(w)
        w.start()

    def _on_check_done(self, ok, msg):
        self._workers = [w for w in self._workers if w.isRunning()]
        self._check_btn.setEnabled(True)
        self._check_btn.setText("Detect Fastboot Device")
        # msg is the list repr from _Worker — re-fetch
        devices = adb.fastboot_devices()
        if devices:
            self._status_label.setText(f"Fastboot device: {devices[0]}")
            self._reboot_sys_btn.setEnabled(True)
            self._reboot_rec_btn.setEnabled(True)
            self._reboot_bl_btn.setEnabled(True)
            self._flash_btn.setEnabled(True)
        else:
            self._status_label.setText("No fastboot device found")
            self._reboot_sys_btn.setEnabled(False)
            self._reboot_rec_btn.setEnabled(False)
            self._reboot_bl_btn.setEnabled(False)
            self._flash_btn.setEnabled(False)

    def _reboot_system(self):
        ok, msg = adb.fastboot_reboot_system()
        if ok:
            self._status_label.setText("Rebooting to system...")
            self._reboot_sys_btn.setEnabled(False)
            self._reboot_rec_btn.setEnabled(False)
            self._reboot_bl_btn.setEnabled(False)
            self._flash_btn.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", msg)

    def _reboot_recovery(self):
        ok, msg = adb.fastboot_reboot_recovery()
        if ok:
            self._status_label.setText("Rebooting to recovery...")
        else:
            QMessageBox.critical(self, "Error", msg)

    def _reboot_bootloader(self):
        ok, msg = adb.fastboot_reboot_bootloader()
        if not ok:
            QMessageBox.critical(self, "Error", msg)

    def _flash_image(self):
        partition, ok = QInputDialog.getText(
            self, "Flash", "Partition name:", text="boot"
        )
        if not ok or not partition:
            return
        img_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.img *.bin);;All Files (*)"
        )
        if not img_path:
            return
        reply = QMessageBox.question(
            self, "Flash",
            f"Flash {partition} with:\n{img_path}\n\nThis may brick your device!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._flash_btn.setEnabled(False)
        self._flash_btn.setText("Flashing...")
        w = _Worker(adb.fastboot_flash, partition, img_path)
        w.finished.connect(self._on_flash_done)
        self._workers.append(w)
        w.start()

    def _on_flash_done(self, ok, msg):
        self._workers = [w for w in self._workers if w.isRunning()]
        self._flash_btn.setEnabled(True)
        self._flash_btn.setText("Flash Image...")
        if ok:
            QMessageBox.information(self, "Flash", "Flash completed successfully!")
        else:
            QMessageBox.critical(self, "Flash Failed", msg)


class AppsGroup(QGroupBox):
    """App management: list, launch, uninstall."""

    def __init__(self, parent=None):
        super().__init__("Apps", parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self._list_btn = QPushButton("App Manager")
        self._list_btn.setObjectName("accent")
        self._list_btn.clicked.connect(self._open_manager)
        layout.addWidget(self._list_btn)

    def _open_manager(self):
        dlg = AppManagerDialog(self)
        dlg.exec()


class AppManagerDialog(QDialog):
    """Dialog for managing installed apps."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("App Manager")
        self.setMinimumSize(500, 600)
        self._workers = []
        self._init_ui()
        self._load_apps()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search apps...")
        self._search.textChanged.connect(self._filter_apps)
        layout.addWidget(self._search)

        self._list = QListWidget()
        layout.addWidget(self._list)

        btn_row = QHBoxLayout()

        self._launch_btn = QPushButton("Launch")
        self._launch_btn.setObjectName("success")
        self._launch_btn.clicked.connect(self._launch)
        btn_row.addWidget(self._launch_btn)

        self._uninstall_btn = QPushButton("Uninstall")
        self._uninstall_btn.setObjectName("danger")
        self._uninstall_btn.clicked.connect(self._uninstall)
        btn_row.addWidget(self._uninstall_btn)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._load_apps)
        btn_row.addWidget(self._refresh_btn)

        layout.addLayout(btn_row)

    def _load_apps(self):
        self._list.clear()
        self._refresh_btn.setEnabled(False)
        self._refresh_btn.setText("Loading...")
        w = _Worker(adb.list_packages, True)
        w.finished.connect(self._on_apps_loaded)
        self._workers.append(w)
        w.start()

    def _on_apps_loaded(self, ok, msg):
        self._workers = [w for w in self._workers if w.isRunning()]
        self._refresh_btn.setEnabled(True)
        self._refresh_btn.setText("Refresh")
        self._list.clear()
        if ok:
            # msg is the list repr, re-fetch properly
            packages = adb.list_packages(third_party=True)
            for pkg in packages:
                self._list.addItem(pkg)

    def _filter_apps(self, text: str):
        for i in range(self._list.count()):
            item = self._list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _launch(self):
        item = self._list.currentItem()
        if not item:
            return
        ok, msg = adb.launch_app(item.text())
        if not ok:
            QMessageBox.critical(self, "Error", msg)

    def _uninstall(self):
        item = self._list.currentItem()
        if not item:
            return
        pkg = item.text()
        reply = QMessageBox.question(
            self, "Uninstall", f"Uninstall {pkg}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = adb.uninstall_app(pkg)
            if ok:
                self._load_apps()
            else:
                QMessageBox.critical(self, "Error", msg)


class ScrcpySettingsGroup(QGroupBox):
    """scrcpy quality/performance settings."""

    def __init__(self, parent=None):
        super().__init__("Mirror Settings", parent)
        self._init_ui()

    def _init_ui(self):
        from PyQt6.QtWidgets import QSlider
        layout = QVBoxLayout(self)

        self._fps_label = QLabel("Max FPS: 60")
        layout.addWidget(self._fps_label)

        self._fps_slider = QSlider(Qt.Orientation.Horizontal)
        self._fps_slider.setRange(15, 120)
        self._fps_slider.setValue(60)
        self._fps_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._fps_slider.setTickInterval(15)
        self._fps_slider.valueChanged.connect(lambda v: self._fps_label.setText(f"Max FPS: {v}"))
        layout.addWidget(self._fps_slider)

        self._bitrate_label = QLabel("Video Bitrate: 8M")
        layout.addWidget(self._bitrate_label)

        self._bitrate_slider = QSlider(Qt.Orientation.Horizontal)
        self._bitrate_slider.setRange(1, 32)
        self._bitrate_slider.setValue(8)
        self._bitrate_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._bitrate_slider.setTickInterval(4)
        self._bitrate_slider.valueChanged.connect(lambda v: self._bitrate_label.setText(f"Video Bitrate: {v}M"))
        layout.addWidget(self._bitrate_slider)

    @property
    def max_fps(self) -> int:
        return self._fps_slider.value()

    @property
    def video_bitrate(self) -> str:
        return f"{self._bitrate_slider.value()}M"


class LeftPanel(QWidget):
    """The complete left panel with all button groups."""

    def __init__(self, scrcpy: ScrcpyManager, parent=None):
        super().__init__(parent)
        self._scrcpy = scrcpy
        self.setFixedWidth(300)
        self._init_ui()

    def _init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("PhoneHub")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.connection = ConnectionGroup(self._scrcpy)
        layout.addWidget(self.connection)

        self.files = FileGroup()
        layout.addWidget(self.files)

        self.screen = ScreenGroup()
        layout.addWidget(self.screen)

        self.device = DeviceGroup()
        layout.addWidget(self.device)

        self.bootloader = BootloaderGroup()
        layout.addWidget(self.bootloader)

        self.apps = AppsGroup()
        layout.addWidget(self.apps)

        self.mirror_settings = ScrcpySettingsGroup()
        layout.addWidget(self.mirror_settings)

        layout.addStretch()

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
