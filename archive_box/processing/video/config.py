from typing import List, NamedTuple


CODECS = [
    "h264", # aac audio
    "h265", # aac audio
    "vp9", # opus audio
    "av1", # opus audio
]


class TargetRepresentation(NamedTuple):
    """Parameters for a target representation of a video + audio file.

    Simplifies some parameters to help provide "good defaults":

    - Aspect ratio is automatically preserved.
    - Bitrate is given as a total value. We compute the split between video + audio bitrates automatically.
    - Only video codec can be selected. We select the best matching audio codec.
    """

    height: int
    # total bitrate, including video + audio
    bitrate_kbits: float
    # one of CODECS
    codec: str

    @staticmethod
    def for_quality(qc: str, codec: str) -> 'TargetRepresentation':
        """Returns a TargetRepresentation with good defaults for the given quality class."""
        if codec not in CODECS:
            raise RuntimeError("Unknown codec {}".format(codec))

        #if qc == "180p":
        #    pass
        #elif qc == "240p":
        #    pass
        if qc == "360p":
            return TargetRepresentation(360, 300.0, codec)
        elif qc == "480p":
            return TargetRepresentation(480, 500.0, codec)
        elif qc == "720p":
            return TargetRepresentation(720, 800.0, codec)
        elif qc == "1080p":
            return TargetRepresentation(1080, 1500.0, codec)
        #elif qc == "1440p":
        #    pass
        #elif qc == "2160p" || qc == "4k":
        #    pass
        else:
            raise RuntimeError("Unknown quality class {}".format(qc))


class TranscodeConfig(NamedTuple):
    # desired representations
    representations: List[TargetRepresentation]

    # keep not only the transcoded versions, but also the original file
    keep_original: bool = True

    # allow original to take the place of a transcoded version, if it is "close enough"
    skip_matching: bool = False
