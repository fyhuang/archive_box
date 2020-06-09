import unittest

from .transcode import *
from .config import *

class ReprSimilarTests(unittest.TestCase):
    def test_height(self) -> None:
        self.assertFalse(repr_similar(
            TargetRepresentation(height=360, bitrate_kbits=200, codec="h264"),
            TargetRepresentation(height=480, bitrate_kbits=200, codec="h264"),
        ))

        self.assertTrue(repr_similar(
            TargetRepresentation(height=500, bitrate_kbits=400, codec="h264"),
            TargetRepresentation(height=520, bitrate_kbits=400, codec="h264"),
        ))

    def test_bitrate(self) -> None:
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

    def test_codec(self) -> None:
        self.assertFalse(repr_similar(
            TargetRepresentation(height=480, bitrate_kbits=200, codec="h264"),
            TargetRepresentation(height=480, bitrate_kbits=200, codec="av1"),
        ))

        self.assertTrue(repr_similar(
            TargetRepresentation(height=480, bitrate_kbits=200, codec="av1"),
            TargetRepresentation(height=480, bitrate_kbits=200, codec="av1"),
        ))


class TranscodeAllTests(unittest.TestCase):
    def setUp(self) -> None:
        self.calls: List[Tuple[Path, Path, TargetRepresentation]] = []

    def mock_transcode_one(self, input_path, output_path, target_repr) -> None:
        self.calls.append((input_path, output_path, target_repr))

    def test_all_smaller(self) -> None:
        source_repr = TargetRepresentation(2160, 20000, "h264")
        config = TranscodeConfig(representations=[
            TargetRepresentation(height=1080, bitrate_kbits=10000, codec="av1"),
            TargetRepresentation(height=720, bitrate_kbits=4000, codec="av1"),
            TargetRepresentation(height=360, bitrate_kbits=500, codec="av1"),
        ], keep_original=True)

        outputs = transcode_all(Path("input.mp4"), Path("output"), config, lambda p: source_repr, self.mock_transcode_one)
        self.assertEqual([
            (Path("input.mp4"), Path("output/1080p_10000k_av1.webm"), config.representations[0]),
            (Path("input.mp4"), Path("output/720p_4000k_av1.webm"), config.representations[1]),
            (Path("input.mp4"), Path("output/360p_500k_av1.webm"), config.representations[2]),
        ], self.calls)

        self.assertEqual({
            config.representations[0]: Path("output/1080p_10000k_av1.webm"),
            config.representations[1]: Path("output/720p_4000k_av1.webm"),
            config.representations[2]: Path("output/360p_500k_av1.webm"),
            "original": Path("input.mp4"),
        }, outputs)

    def test_skip_some(self) -> None:
        source_repr = TargetRepresentation(720, 1000, "h264")
        config = TranscodeConfig(representations=[
            TargetRepresentation(height=1080, bitrate_kbits=10000, codec="av1"),
            TargetRepresentation(height=720, bitrate_kbits=4000, codec="av1"),
            TargetRepresentation(height=360, bitrate_kbits=500, codec="av1"),
        ], keep_original=True)

        outputs = transcode_all(Path("input.mp4"), Path("output"), config, lambda p: source_repr, self.mock_transcode_one)
        self.assertEqual([
            # skip first representation since we don't upscale
            # skip second representation since we don't re-encode at higher bitrate
            (Path("input.mp4"), Path("output/360p_500k_av1.webm"), config.representations[2]),
        ], self.calls)

        self.assertEqual({
            config.representations[2]: Path("output/360p_500k_av1.webm"),
            "original": Path("input.mp4"),
        }, outputs)

    def test_reuse_input(self) -> None:
        source_repr = TargetRepresentation(720, 1000, "h264")
        config = TranscodeConfig(representations=[
            TargetRepresentation(height=720, bitrate_kbits=950, codec="h264"),
        ], skip_similar=True, keep_original=True)

        outputs = transcode_all(Path("input.mp4"), Path("output"), config, lambda p: source_repr, self.mock_transcode_one)
        self.assertEqual([], self.calls)

        self.assertEqual({
            config.representations[0]: Path("input.mp4"),
            "original": Path("input.mp4"),
        }, outputs)

    def test_dont_keep_original(self) -> None:
        source_repr = TargetRepresentation(720, 1000, "h264")
        config = TranscodeConfig(representations=[
            TargetRepresentation(height=360, bitrate_kbits=500, codec="av1"),
        ], keep_original=False)

        outputs = transcode_all(Path("input.mp4"), Path("output"), config, lambda p: source_repr, self.mock_transcode_one)
        self.assertEqual([
            (Path("input.mp4"), Path("output/360p_500k_av1.webm"), config.representations[0]),
        ], self.calls)

        self.assertEqual({
            config.representations[0]: Path("output/360p_500k_av1.webm"),
            # no entry for "original"
        }, outputs)
