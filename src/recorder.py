import os

from pathlib import Path
from tempfile import mkstemp

from osr2mp4.osr2mp4 import Osr2mp4


def record(beatmap: Path, replay: Path) -> Path:
    _, output = mkstemp(suffix=".mp4")
    data = {
        "osu! path": "/",
        "Skin path": os.environ["OSU_SKIN_PATH"],
        "Beatmap path": beatmap.as_posix(),
        ".osr path": replay.as_posix(),
        "Default skin path": os.environ["OSU_SKIN_PATH"],
        "Output path": output,
        "Width": 1280,
        "Height": 720,
        "FPS": 60,
        "Start time": 0,
        "End time": -1,
        "Video codec": "XVID",
        "Process": 2,
        "ffmpeg path": "ffmpeg",
    }
    settings = {
        "Show scoreboard": False,
        "Song volume": 100,
        "Effect volume": 100,
        "Use FFmpeg video writer": True,
        "api key": "",
    }
    osr = Osr2mp4(data, settings)
    osr.startall()
    osr.joinall()
    return Path(output)
