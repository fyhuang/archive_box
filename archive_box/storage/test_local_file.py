import unittest
import tempfile
from pathlib import Path

from . import local_file
from .local_file import *
from .stored_data import *

from archive_box.sdid import file_to_sdid

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

    def test_upload_contains_stat(self) -> None:
        lfs = LocalFileStorage(self.path / "store")
        sdid = file_to_sdid(self.path / "test.txt")
        lfs.upload(sdid, self.path / "test.txt")
        self.assertTrue(lfs.contains(sdid))

        stat = lfs.download_stat(sdid)
        self.assertEqual(13, stat.size_bytes)
        ts_diff = datetime.datetime.now() - stat.upload_time
        self.assertTrue(ts_diff <= datetime.timedelta(minutes=1))

    def test_download_bytes(self) -> None:
        lfs = LocalFileStorage(self.path / "store")
        sdid = file_to_sdid(self.path / "test.txt")
        lfs.upload(sdid, self.path / "test.txt")

        with lfs.download_bytes(sdid) as f:
            self.assertEqual(b'Hello, world!', f.read())
        with lfs.download_bytes(sdid, (0, 4)) as f:
            self.assertEqual(b'Hello', f.read())
        with lfs.download_bytes(sdid, (7, 12)) as f:
            self.assertEqual(b'world!', f.read())

    def test_download_to(self) -> None:
        lfs = LocalFileStorage(self.path / "store")
        sdid = file_to_sdid(self.path / "test.txt")
        lfs.upload(sdid, self.path / "test.txt")

        lfs.download_to(sdid, self.path / "out.txt")
        with (self.path / "out.txt").open("r") as f:
            self.assertEqual("Hello, world!", f.read())
