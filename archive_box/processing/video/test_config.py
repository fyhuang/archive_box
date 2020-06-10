import unittest

from .config import *

class TargetRepresentationTests(unittest.TestCase):
    def test_comparisons(self):
        from .config import TargetRepresentation as TR
        # codec
        self.assertTrue(TR(360, 1000, "h264") < TR(360, 1000, "av1"))

        # height
        self.assertTrue(TR(360, 1000, "h264") < TR(720, 1000, "h264"))
        self.assertTrue(TR(1080, 1000, "h264") > TR(720, 1000, "h264"))

        # bitrate
        self.assertTrue(TR(1080, 1000, "h264") < TR(1080, 1100, "h264"))
        self.assertTrue(TR(1080, 2000, "h264") >= TR(1080, 1100, "h264"))

    def test_encoding(self):
        from .config import TargetRepresentation as TR
        self.assertEqual(TR(1080, 1000, "av1"), TR.from_str("1080p_1000k_av1"))
        self.assertEqual("720p_200k_vp9", TR(720, 200, "vp9").to_str())
