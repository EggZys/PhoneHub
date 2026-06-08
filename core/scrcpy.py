"""scrcpy process management."""

import subprocess
import os
from typing import Optional

from core.runtime import scrcpy_path


SCRCPY_PATH = str(scrcpy_path())


class ScrcpyManager:
    """Manages the scrcpy process."""

    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None

    @property
    def running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def start(
        self,
        max_fps: int = 60,
        video_bitrate: str = "8M",
        stay_awake: bool = True,
        screen_off: bool = False,
        no_audio: bool = False,
        always_on_top: bool = False,
        extra_args: list[str] | None = None,
    ) -> tuple[bool, str]:
        """Start scrcpy with given options."""
        if self.running:
            return False, "scrcpy is already running"

        args = [
            SCRCPY_PATH,
            "--max-fps", str(max_fps),
            "-b", video_bitrate,
        ]
        if stay_awake:
            args.append("--keep-active")
        if screen_off:
            args.append("--turn-screen-off")
        if no_audio:
            args.append("--no-audio")
        if always_on_top:
            args.append("--always-on-top")
        if extra_args:
            args.extend(extra_args)

        try:
            self._proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(SCRCPY_PATH),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return True, "scrcpy started"
        except FileNotFoundError:
            return False, f"scrcpy not found at {SCRCPY_PATH}"
        except Exception as e:
            return False, str(e)

    def stop(self):
        """Stop scrcpy."""
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None

    def __del__(self):
        self.stop()
