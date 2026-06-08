"""Runtime helpers for locating bundled external tools."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def is_frozen() -> bool:
    """Return True when running from a PyInstaller build."""
    return bool(getattr(sys, "frozen", False))


def resource_root() -> Path:
    """Return the directory that contains bundled app resources."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[1]


def executable_root() -> Path:
    """Return the directory that contains the application executable."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _iter_candidates(executable: str, bundled_subdir: str, extra_dirs: list[Path]) -> list[Path]:
    candidates: list[Path] = [
        resource_root() / bundled_subdir / executable,
        executable_root() / bundled_subdir / executable,
        executable_root() / executable,
    ]
    candidates.extend(path / executable for path in extra_dirs)

    system_path = shutil.which(executable)
    if system_path:
        candidates.append(Path(system_path))

    return candidates


def _first_existing(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0]


def _windows_local_appdata() -> Path | None:
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        return None
    return Path(local_appdata)


def adb_path() -> Path:
    """Resolve the best available adb executable."""
    extra_dirs = []
    configured = os.environ.get("PHONEHUB_SCRCPY_DIR")
    if configured:
        extra_dirs.append(Path(configured))

    local_appdata = _windows_local_appdata()
    if local_appdata:
        extra_dirs.append(local_appdata / "Android" / "Sdk" / "platform-tools")

    extra_dirs.extend(
        [
            Path(r"C:\scrcpy"),
            Path(r"C:\adb"),
        ]
    )
    return _first_existing(_iter_candidates("adb.exe", "tools/scrcpy", extra_dirs))


def fastboot_path() -> Path:
    """Resolve the best available fastboot executable."""
    extra_dirs = []
    for env_var in ("PHONEHUB_PLATFORM_TOOLS_DIR", "ANDROID_SDK_ROOT", "ANDROID_HOME"):
        configured = os.environ.get(env_var)
        if configured:
            base = Path(configured)
            extra_dirs.append(base if base.name == "platform-tools" else base / "platform-tools")

    local_appdata = _windows_local_appdata()
    if local_appdata:
        extra_dirs.append(local_appdata / "Android" / "Sdk" / "platform-tools")

    extra_dirs.append(Path(r"C:\adb"))
    return _first_existing(_iter_candidates("fastboot.exe", "tools/platform-tools", extra_dirs))


def scrcpy_path() -> Path:
    """Resolve the best available scrcpy executable."""
    extra_dirs = []
    configured = os.environ.get("PHONEHUB_SCRCPY_DIR")
    if configured:
        extra_dirs.append(Path(configured))

    extra_dirs.extend(
        [
            Path(r"C:\scrcpy"),
            Path(r"C:\adb"),
        ]
    )
    return _first_existing(_iter_candidates("scrcpy.exe", "tools/scrcpy", extra_dirs))
