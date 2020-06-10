import functools
import re
from typing import List, NamedTuple


_TR_ENCODED_RE = re.compile(r'(?P<height>\d+)p_(?P<bitrate>\d+)k_(?P<codec>[\w\d]+)')


CODECS = [
    "h264", # aac audio
    "h265", # aac audio
    "vp9", # opus audio
    "av1", # opus audio
]


@functools.total_ordering
class TargetRepresentation(NamedTuple):
    """Parameters for a target representation of a video + audio file.

    Simplifies some parameters to help provide "good defaults":

    - Aspect ratio is automatically preserved.
    - Bitrate is given as a total value. We compute the split between video + audio bitrates automatically.
    - Only video codec can be selected. We select the best matching audio codec.
    """

    height: int
    # total bitrate, including video + audio
    bitrate_kbits: int
    # one of CODECS
    codec: str

    # TODO(fyhuang): from_dict function to support quality shortcuts

    def __lt__(self, other):
        # compare by codec first, then height, then bitrate
        self_tuple = (CODECS.index(self.codec), self.height, self.bitrate_kbits)
        other_tuple = (CODECS.index(other.codec), other.height, other.bitrate_kbits)
        return self_tuple < other_tuple

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
            return TargetRepresentation(360, bitrate_kbits=300, codec=codec)
        elif qc == "480p":
            return TargetRepresentation(480, bitrate_kbits=500, codec=codec)
        elif qc == "720p":
            return TargetRepresentation(720, bitrate_kbits=800, codec=codec)
        elif qc == "1080p":
            return TargetRepresentation(1080, bitrate_kbits=1500, codec=codec)
        #elif qc == "1440p":
        #    pass
        #elif qc == "2160p" || qc == "4k":
        #    pass
        else:
            raise RuntimeError("Unknown quality class {}".format(qc))

    @staticmethod
    def from_str(encoded: str) -> 'TargetRepresentation':
        m = _TR_ENCODED_RE.match(encoded)
        if m is None:
            raise ValueError("\"{}\" is not a valid TargetRepresentation".format(encoded))
        return TargetRepresentation(int(m.group("height")), int(m.group("bitrate")), m.group("codec"))

    def to_str(self) -> str:
        return "{}p_{}k_{}".format(self.height, self.bitrate_kbits, self.codec)


class TranscodeConfig(NamedTuple):
    # desired representations
    representations: List[TargetRepresentation]

    # Allow original to take the place of a transcoded version, if it is "close enough".
    skip_similar: bool = False

    # Keep not only the transcoded versions, but also the original file. If the original was reused as
    # one of the output representations (see skip_similar), the original will be kept even if
    # keep_original is False.
    keep_original: bool = True
