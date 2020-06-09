import inspect
import shutil
import subprocess
import json
from pathlib import Path
from typing import Mapping

from .config import *


def _find_ffprobe() -> Path:
    import archive_box
    package_path = Path(inspect.getfile(archive_box)).resolve().parent
    root_path = package_path.parent

    extern_ffprobe = root_path / "extern" / "ffmpeg" / "ffprobe"
    if extern_ffprobe.exists() and extern_ffprobe.is_file():
        return extern_ffprobe

    # try using system ffprobe if exists
    system_ffprobe = shutil.which("ffprobe")
    if system_ffprobe is not None:
        return Path(system_ffprobe)

    raise RuntimeError("Could not find ffprobe for transcoding")


def _find_video_stream(info: Mapping) -> Mapping:
    for s in info["streams"]:
        if s["codec_type"] == "video":
            return s
    raise RuntimeError("No video stream in file")


def guess_file_repr(input_file: Path) -> TargetRepresentation:
    ffprobe = str(_find_ffprobe())
    args = [ffprobe,
            "-loglevel", "error",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(input_file),
            ]
    #print(args)
    info_str = subprocess.check_output(args)
    info = json.loads(info_str)

    # compute total bitrate from container
    bitrate_kbits = int(round(float(info["format"]["bit_rate"]) / 1000))

    # find the video stream to get codec and height
    video_info = _find_video_stream(info)
    return TargetRepresentation(video_info["height"], bitrate_kbits, video_info["codec_name"])
