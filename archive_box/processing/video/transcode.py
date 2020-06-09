import os
import inspect
import shutil
import subprocess
from pathlib import Path
from typing import Union, List, Tuple, Dict, Callable
from typing_extensions import Literal

from . import ffmpeg_params, ffprobe
from .config import *


OutputKey = Union[Literal["original"], TargetRepresentation]
OutputsDict = Dict[OutputKey, Path]


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


def _split_bitrate_h264(total_bitrate: float) -> Tuple[float, float]:
    audio = min(150.0, total_bitrate * 0.15)
    return (total_bitrate - audio, audio)


def _split_bitrate_av1(total_bitrate: float) -> Tuple[float, float]:
    audio = min(150.0, total_bitrate * 0.1)
    return (total_bitrate - audio, audio)


def _container_from_codec(codec: str) -> str:
    if codec in ("h264", "h265"):
        return "mp4"
    elif codec in ("vp9", "av1"):
        return "webm"
    else:
        raise RuntimeError("Unknown codec {}".format(codec))


# TODO(fyhuang): maybe combine this and `should_create_repr` into a general "compare" func
def repr_similar(source_repr: TargetRepresentation, target_repr: TargetRepresentation) -> bool:
    if source_repr.codec != target_repr.codec:
        return False
    height_diff = abs(source_repr.height - target_repr.height)
    if height_diff > 100:
        return False
    bitrate_diff = abs(source_repr.bitrate_kbits - target_repr.bitrate_kbits)
    bitrate_diff_relative = bitrate_diff / min(source_repr.bitrate_kbits, target_repr.bitrate_kbits)
    if bitrate_diff_relative > 0.1:
        return False

    return True


def should_create_repr(source_repr: TargetRepresentation, target_repr: TargetRepresentation) -> bool:
    # no need to upscale while transcoding
    if target_repr.height > source_repr.height + 100:
        return False

    # no need to increase bitrate while transcoding
    if (target_repr.bitrate_kbits / source_repr.bitrate_kbits) > 1.1:
        return False
    
    return True


def transcode_one(input_file: Path, output_file: Path, target_repr: TargetRepresentation):
    ffmpeg = str(_find_ffmpeg())

    # pick params based on codec
    if target_repr.codec == "h264":
        raise NotImplementedError()
    elif target_repr.codec == "h265":
        raise NotImplementedError()
    elif target_repr.codec == "vp9":
        raise NotImplementedError()
    elif target_repr.codec == "av1":
        video_bitrate, audio_bitrate = _split_bitrate_av1(target_repr.bitrate_kbits)
        pass1_params = ffmpeg_params.av1_params_1p(video_bitrate)
        pass2_params = ffmpeg_params.av1_params_2p(video_bitrate)
        audio_params = ffmpeg_params.opus_params(audio_bitrate)

    scale_params = ["-vf", "scale=-1:{}".format(target_repr.height)]

    # first pass encode
    ffmpeg_args = [ffmpeg, "-y", "-i", str(input_file)] + scale_params + pass1_params
    # no need for audio on first pass, and we can ignore the video output
    ffmpeg_args += ["-an", os.devnull]
    print(ffmpeg_args)
    subprocess.check_call(ffmpeg_args)

    # second pass encode
    ffmpeg_args = [ffmpeg, "-y", "-i", str(input_file)] + scale_params + pass2_params + audio_params
    ffmpeg_args += [str(output_file)]
    print(ffmpeg_args)
    subprocess.check_call(ffmpeg_args)


def transcode_all(
        input_file: Path,
        output_dir: Path,
        config: TranscodeConfig,
        guess_repr_func: Callable[[Path], TargetRepresentation] = ffprobe.guess_file_repr,
        transcode_one_func: Callable[[Path, Path, TargetRepresentation], None] = transcode_one,
        ) -> OutputsDict:
    source_repr = guess_repr_func(input_file)

    filenames: OutputsDict = {}
    for repr in config.representations:
        if repr_similar(source_repr, repr):
            if config.skip_similar:
                filenames[repr] = input_file
                continue

        if not should_create_repr(source_repr, repr):
            continue

        output_file = output_dir / "{}.{}".format(repr.as_filename_component(), _container_from_codec(repr.codec))
        transcode_one_func(input_file, output_file, repr)
        filenames[repr] = output_file

    if config.keep_original:
        filenames["original"] = input_file

    return filenames
