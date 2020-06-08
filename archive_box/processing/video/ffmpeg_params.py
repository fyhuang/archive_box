from typing import List


def av1_params_1p(video_bitrate: float) -> List[str]:
    return ["-c:v", "libaom-av1",
            "-strict", "experimental",
            "-pass", "1",
            # low quality for 1st pass is fine
            "-cpu-used", "8",
            "-b:v", "{}k".format(video_bitrate),
            "-f", "matroska",
            ]


def av1_params_2p(video_bitrate: float) -> List[str]:
    return ["-c:v", "libaom-av1",
            "-strict", "experimental",
            "-pass", "2",
            # low marginal quality returns below 5, see
            # <https://www.streamingmedia.com/Articles/ReadArticle.aspx?ArticleID=130284>
            "-cpu-used", "5",
            "-b:v", "{}k".format(video_bitrate),
            "-f", "matroska",
            ]


def opus_params(audio_bitrate: float) -> List[str]:
    low_br_args = []
    if audio_bitrate <= 50.0:
        low_br_args += [
            # longer frame for hopefully better encode quality
            "-frame_duration", "60",
            # favor speech intelligibility
            "-application", "voip",
        ]
    if audio_bitrate <= 30.0:
        low_br_args += [
            # force mono
            "-ac", "1",
        ]
    return ["-c:a", "libopus", "-b:a", "{}k".format(audio_bitrate)] + low_br_args
