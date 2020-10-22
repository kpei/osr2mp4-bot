import os
import sys

from pathlib import Path
from shutil import rmtree
from tempfile import mkstemp

from osr2mp4.osr2mp4 import Osr2mp4


def record(mapset: Path, replay: Path) -> Path:
    _, output = mkstemp(dir=os.environ["VIDEO_DIR"], suffix=".mp4")
    data = {
        "osu! path": "/",
        "Skin path": os.environ["OSU_SKIN_PATH"],
        "Beatmap path": mapset.as_posix(),
        ".osr path": replay.as_posix(),
        "Default skin path": os.environ["OSU_SKIN_PATH"],
        "Output path": output,
        "Width": 1920,
        "Height": 1080,
        "FPS": 60,
        "Start time": 0,
        "End time": -1,
        "Video codec": "mp4v",
        "Process": 2,
        "ffmpeg path": "ffmpeg",
    }
    settings = {
        "Global leaderboard": True,
        "Song volume": 100,
        "Effect volume": 100,
        "Enable PP counter": True,
        "api key": os.environ["OSU_API_KEY"],
    }
    hostname = os.getenv("HOSTNAME", "unknown")
    logs = os.path.join(os.environ["LOG_DIR"], f"osr2mp4-{hostname}.log")
    hook = sys.excepthook
    osr = Osr2mp4(data, settings, logtofile=True, logpath=logs)
    sys.excepthook = hook
    osr.startall()
    osr.joinall()
    osr.cleanup()
    rmtree(mapset)
    replay.unlink()
    return Path(output)
