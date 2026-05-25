"""ADB command wrappers for device management."""

import subprocess
import os
import tempfile
import zipfile
from pathlib import Path

ADB_PATH = r"C:\scrcpy\adb.exe"
FASTBOOT_PATH = r"C:\Users\EggZys\AppData\Local\Android\Sdk\platform-tools\fastboot.exe"


def _run(args: list[str], timeout: int = 60, capture: bool = True) -> subprocess.CompletedProcess:
    """Run an ADB command and return the result."""
    cmd = [ADB_PATH] + args
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def _run_async(args: list[str]) -> subprocess.Popen:
    """Start an ADB command asynchronously."""
    cmd = [ADB_PATH] + args
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


# ── Device ──────────────────────────────────────────────────────────

def get_devices() -> list[str]:
    """Return list of connected device serials."""
    result = _run(["devices"])
    devices = []
    for line in result.stdout.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def get_device_info() -> dict[str, str]:
    """Get device model, Android version, and serial."""
    info = {}
    for key, prop in [("model", "ro.product.model"), ("version", "ro.build.version.release"), ("sdk", "ro.build.version.sdk")]:
        r = _run(["shell", "getprop", prop])
        info[key] = r.stdout.strip() if r.returncode == 0 else "N/A"
    r = _run(["get-serialno"])
    info["serial"] = r.stdout.strip() if r.returncode == 0 else "N/A"
    return info


def get_battery_info() -> dict[str, str]:
    """Get battery level and status."""
    r = _run(["shell", "dumpsys", "battery"])
    info = {}
    for line in r.stdout.splitlines():
        line = line.strip()
        if ":" in line:
            key, val = line.split(":", 1)
            key, val = key.strip(), val.strip()
            if key in ("level", "status", "temperature", "health"):
                info[key.lower()] = val
    return info


# ── APK Install ─────────────────────────────────────────────────────

def install_apk(apk_path: str) -> tuple[bool, str]:
    """Install an APK file to the device."""
    if not os.path.isfile(apk_path):
        return False, f"File not found: {apk_path}"
    ext = Path(apk_path).suffix.lower()
    if ext == ".xapk":
        return install_xapk(apk_path)
    r = _run(["install", "-r", apk_path], timeout=300)
    ok = r.returncode == 0 and "Success" in r.stdout
    return ok, r.stdout.strip() if ok else r.stderr.strip() or r.stdout.strip()


def install_xapk(xapk_path: str) -> tuple[bool, str]:
    """Install an XAPK file (ZIP containing split APKs)."""
    if not os.path.isfile(xapk_path):
        return False, f"File not found: {xapk_path}"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(xapk_path, "r") as zf:
                zf.extractall(tmp)

            # Find all .apk files in extracted contents
            apk_files = sorted(Path(tmp).rglob("*.apk"))
            if not apk_files:
                return False, "No APK files found inside XAPK"

            apk_args = [str(p) for p in apk_files]
            r = _run(["install-multiple", "-r"] + apk_args, timeout=600)
            ok = r.returncode == 0 and "Success" in r.stdout
            return ok, r.stdout.strip() if ok else r.stderr.strip() or r.stdout.strip()
    except zipfile.BadZipFile:
        return False, "Invalid XAPK file (not a valid ZIP)"
    except Exception as e:
        return False, str(e)


# ── Fastboot ────────────────────────────────────────────────────────

def _fb_run(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a fastboot command."""
    cmd = [FASTBOOT_PATH] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def fastboot_devices() -> list[str]:
    """List devices in fastboot mode."""
    r = _fb_run(["devices"])
    devices = []
    for line in r.stdout.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "fastboot":
            devices.append(parts[0])
    return devices


def fastboot_reboot_system() -> tuple[bool, str]:
    """Reboot from fastboot to system."""
    r = _fb_run(["reboot"], timeout=30)
    ok = r.returncode == 0
    return ok, r.stdout.strip() if ok else r.stderr.strip()


def fastboot_reboot_recovery() -> tuple[bool, str]:
    """Reboot from fastboot to recovery."""
    r = _fb_run(["reboot", "recovery"], timeout=30)
    ok = r.returncode == 0
    return ok, r.stdout.strip() if ok else r.stderr.strip()


def fastboot_reboot_bootloader() -> tuple[bool, str]:
    """Reboot from fastboot back to bootloader."""
    r = _fb_run(["reboot", "bootloader"], timeout=30)
    ok = r.returncode == 0
    return ok, r.stdout.strip() if ok else r.stderr.strip()


def fastboot_flash(partition: str, img_path: str) -> tuple[bool, str]:
    """Flash an image to a partition."""
    if not os.path.isfile(img_path):
        return False, f"File not found: {img_path}"
    r = _fb_run(["flash", partition, img_path], timeout=600)
    ok = r.returncode == 0
    return ok, r.stdout.strip() if ok else r.stderr.strip()


def fastboot_getvar(var: str) -> str:
    """Get a fastboot variable (e.g. 'product', 'version')."""
    r = _fb_run(["getvar", var])
    # fastboot getvar outputs to stderr
    output = r.stderr.strip() or r.stdout.strip()
    for line in output.splitlines():
        if line.startswith(f"{var}:"):
            return line.split(":", 1)[1].strip()
    return output


# ── File Transfer ───────────────────────────────────────────────────

def push_file(local_path: str, remote_dir: str = "/sdcard/Download/") -> tuple[bool, str]:
    """Push a file to the device."""
    if not os.path.isfile(local_path):
        return False, f"File not found: {local_path}"
    r = _run(["push", local_path, remote_dir], timeout=300)
    ok = r.returncode == 0
    return ok, r.stdout.strip() if ok else r.stderr.strip()


def pull_file(remote_path: str, local_dir: str) -> tuple[bool, str]:
    """Pull a file from the device."""
    r = _run(["pull", remote_path, local_dir], timeout=300)
    ok = r.returncode == 0
    return ok, r.stdout.strip() if ok else r.stderr.strip()


def list_directory(remote_path: str = "/sdcard/") -> list[str]:
    """List files in a remote directory."""
    r = _run(["shell", "ls", "-la", remote_path])
    if r.returncode != 0:
        return []
    return r.stdout.strip().splitlines()


# ── Screenshot ──────────────────────────────────────────────────────

def screenshot(save_path: str) -> tuple[bool, str]:
    """Take a screenshot and save locally."""
    cmd = [ADB_PATH, "exec-out", "screencap", "-p"]
    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    if r.returncode != 0:
        return False, r.stderr.decode("utf-8", errors="replace").strip()
    if not r.stdout:
        return False, "Empty screenshot output"
    Path(save_path).write_bytes(r.stdout)
    return True, save_path


# ── Screen Record ───────────────────────────────────────────────────

def screen_record_start(save_path: str, time_limit: int = 180) -> subprocess.Popen:
    """Start screen recording (max 180s). Returns Popen to manage."""
    return _run_async(["shell", "screenrecord", "--time-limit", str(min(time_limit, 180)), "/sdcard/phonehub_record.mp4"])


def screen_record_stop(proc: subprocess.Popen, local_path: str) -> tuple[bool, str]:
    """Stop recording and pull the file."""
    proc.terminate()
    proc.wait(timeout=10)
    # Wait a moment for the file to finalize
    import time
    time.sleep(2)
    r = _run(["pull", "/sdcard/phonehub_record.mp4", local_path], timeout=120)
    _run(["shell", "rm", "/sdcard/phonehub_record.mp4"])
    ok = r.returncode == 0
    return ok, local_path if ok else r.stderr.strip()


# ── Reboot ──────────────────────────────────────────────────────────

def reboot(mode: str = "") -> bool:
    """Reboot device. mode: '', 'recovery', 'bootloader'."""
    args = ["reboot"]
    if mode:
        args.append(mode)
    r = _run(args, timeout=10)
    return r.returncode == 0


# ── Apps ────────────────────────────────────────────────────────────

def list_packages(third_party: bool = True) -> list[str]:
    """List installed packages."""
    args = ["shell", "pm", "list", "packages"]
    if third_party:
        args.append("-3")
    r = _run(args, timeout=30)
    packages = []
    for line in r.stdout.splitlines():
        if line.startswith("package:"):
            packages.append(line.removeprefix("package:").strip())
    return sorted(packages)


def launch_app(package: str, activity: str = "") -> tuple[bool, str]:
    """Launch an app by package name."""
    if activity:
        r = _run(["shell", "am", "start", "-n", f"{package}/{activity}"])
    else:
        r = _run(["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"])
    ok = r.returncode == 0
    return ok, r.stdout.strip() if ok else r.stderr.strip()


def uninstall_app(package: str) -> tuple[bool, str]:
    """Uninstall an app."""
    r = _run(["uninstall", package], timeout=60)
    ok = r.returncode == 0 and "Success" in r.stdout
    return ok, r.stdout.strip() if ok else r.stderr.strip()


def get_app_name(package: str) -> str:
    """Try to get the app label from dumpsys."""
    r = _run(["shell", "dumpsys", "package", package])
    for line in r.stdout.splitlines():
        if "labelRes=" in line:
            # Fallback: just return package name
            return package
    return package


# ── Clipboard ───────────────────────────────────────────────────────

def get_clipboard() -> str:
    """Get clipboard text from device."""
    r = _run(["shell", "cmd", "clipboard", "get"], timeout=10)
    return r.stdout.strip() if r.returncode == 0 else ""


def set_clipboard(text: str) -> bool:
    """Set clipboard text on device."""
    r = _run(["shell", "cmd", "clipboard", "set", text], timeout=10)
    return r.returncode == 0


# ── Input ───────────────────────────────────────────────────────────

def input_keyevent(keycode: str) -> bool:
    """Send a keyevent (e.g. KEYCODE_POWER, KEYCODE_HOME)."""
    r = _run(["shell", "input", "keyevent", keycode])
    return r.returncode == 0


def input_text(text: str) -> bool:
    """Type text on the device."""
    r = _run(["shell", "input", "text", text])
    return r.returncode == 0


# ── Power ───────────────────────────────────────────────────────────

def power_off_screen() -> bool:
    """Turn off the screen (without locking)."""
    return input_keyevent("KEYCODE_POWER")


def wake_screen() -> bool:
    """Wake up the screen."""
    return input_keyevent("KEYCODE_WAKEUP")
