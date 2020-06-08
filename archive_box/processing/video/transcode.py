import os
import inspect
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

from . import ffmpeg_params
from .config import *


def _find_ffmpeg() -> Path:
    import archive_box
    package_path = Path(inspect.getfile(archive_box)).resolve().parent
    root_path = package_path.parent

    extern_ffmpeg = root_path / "extern" / "ffmpeg" / "ffmpeg"
    if extern_ffmpeg.exists() and extern_ffmpeg.is_file():
        return extern_ffmpeg

    # try using system ffmpeg if exists
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg is not None:
        return Path(system_ffmpeg)

    raise RuntimeError("Could not find FFmpeg for transcoding")


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


def _split_bitrate_h264(total_bitrate: float) -> Tuple[float, float]:
    audio = min(150.0, total_bitrate * 0.15)
    return (total_bitrate - audio, audio)


def _split_bitrate_av1(total_bitrate: float) -> Tuple[float, float]:
    audio = min(150.0, total_bitrate * 0.1)
    return (total_bitrate - audio, audio)


def _guess_file_repr(input_file: Path) -> TargetRepresentation:
    ffprobe = str(_find_ffprobe())
    raise NotImplementedError()


def do_transcode(input_file: Path, config: TranscodeConfig) -> None:
    ffmpeg = str(_find_ffmpeg())

    source_repr = _guess_file_repr(input_file)

    for repr in config.representations:
        # TODO(fyhuang): check if we need to produce this representation

        # pick params based on codec
        if repr.codec == "h264":
            raise NotImplementedError()
        elif repr.codec == "h265":
            raise NotImplementedError()
        elif repr.codec == "vp9":
            raise NotImplementedError()
        elif repr.codec == "av1":
            video_bitrate, audio_bitrate = _split_bitrate_av1(repr.bitrate_kbits)
            pass1_params = ffmpeg_params.av1_params_1p(video_bitrate)
            pass2_params = ffmpeg_params.av1_params_2p(video_bitrate)
            audio_params = ffmpeg_params.opus_params(audio_bitrate)

        scale_params = ["-vf", "scale=-1:{}".format(repr.height)]

        # first pass encode
        ffmpeg_args = [ffmpeg, "-y", "-i", str(input_file)] + scale_params + pass1_params
        # no need for audio on first pass, and we can ignore the video output
        ffmpeg_args += ["-an", os.devnull]
        print(ffmpeg_args)
        subprocess.check_call(ffmpeg_args)

        # second pass encode
        ffmpeg_args = [ffmpeg, "-y", "-i", str(input_file)] + scale_params + pass2_params + audio_params
        ffmpeg_args += ["TODO_output.mkv"]
        print(ffmpeg_args)
        subprocess.check_call(ffmpeg_args)
