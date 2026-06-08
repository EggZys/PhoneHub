# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))

scrcpy_dir = Path(os.environ.get("PHONEHUB_SCRCPY_DIR", r"C:\scrcpy"))
platform_tools_dir = Path(
    os.environ.get(
        "PHONEHUB_PLATFORM_TOOLS_DIR",
        local_appdata / "Android" / "Sdk" / "platform-tools",
    )
)

missing_dirs = [str(path) for path in (scrcpy_dir, platform_tools_dir) if not path.exists()]
if missing_dirs:
    raise SystemExit(
        "Missing required tool directories for release build: "
        + ", ".join(missing_dirs)
    )

tools_datas = [
    (str(scrcpy_dir), "tools/scrcpy"),
    (str(platform_tools_dir), "tools/platform-tools"),
]


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=tools_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PhoneHub",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
