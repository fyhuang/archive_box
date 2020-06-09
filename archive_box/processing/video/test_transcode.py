import unittest

from .transcode import *
from .config import *

class TranscodeDecisionTests(unittest.TestCase):
    def test_repr_similar_height(self) -> None:
        self.assertFalse(repr_similar(
            TargetRepresentation(height=360, bitrate_kbits=200, codec="h264"),
            TargetRepresentation(height=480, bitrate_kbits=200, codec="h264"),
        ))

        self.assertTrue(repr_similar(
            TargetRepresentation(height=500, bitrate_kbits=400, codec="h264"),
            TargetRepresentation(height=520, bitrate_kbits=400, codec="h264"),
        ))

    def test_repr_similar_bitrate(self) -> None:
        self.assertFalse(repr_similar(
            TargetRepresentation(height=360, bitrate_kbits=100, codec="h264"),
            TargetRepresentation(height=360, bitrate_kbits=12, codec="h264"),
        ))

        self.assertFalse(repr_similar(
            TargetRepresentation(height=2160, bitrate_kbits=20000, codec="h264"),
            TargetRepresentation(height=2160, bitrate_kbits=23000, codec="h264"),
        ))

        self.assertTrue(repr_similar(
            TargetRepresentation(height=720, bitrate_kbits=10000, codec="h264"),
            TargetRepresentation(height=720, bitrate_kbits=10500, codec="h264"),
        ))

    def test_repr_similar_codec(self) -> None:
        self.assertFalse(repr_similar(
            TargetRepresentation(height=480, bitrate_kbits=200, codec="h264"),
            TargetRepresentation(height=480, bitrate_kbits=200, codec="av1"),
        ))

        self.assertTrue(repr_similar(
            TargetRepresentation(height=480, bitrate_kbits=200, codec="av1"),
            TargetRepresentation(height=480, bitrate_kbits=200, codec="av1"),
        ))
