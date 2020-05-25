import unittest
import tempfile
from pathlib import Path

from . import local_file
from .local_file import *
from .stored_data import *

class LocalFileStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name)
        with (self.path / "test.txt").open("w") as f:
            f.write("Hello, world!")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_common_ancestor(self) -> None:
        self.assertEqual(
            Path("/a/b"),
            local_file._common_ancestor(Path("/a/b/c"), Path("/a/b/def"))
        )

    def test_upload_contains(self) -> None:
        lfs = LocalFileStorage(self.path / "store")
        sdid = file_to_sdid(self.path / "test.txt")
        lfs.upload(sdid, self.path / "test.txt")
        self.assertTrue(lfs.contains(sdid))

    def test_download_bytes(self) -> None:
        lfs = LocalFileStorage(self.path / "store")
        sdid = file_to_sdid(self.path / "test.txt")
        lfs.upload(sdid, self.path / "test.txt")

        with lfs.download_bytes(sdid) as f:
            self.assertEqual(b'Hello, world!', f.read())
