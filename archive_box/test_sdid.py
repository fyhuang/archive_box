import unittest
import hashlib
import tempfile
from pathlib import Path

from .sdid import *


class StoredDataIdTests(unittest.TestCase):
    def test_to_strid(self) -> None:
        sdid = StoredDataId("01", "abc123")
        self.assertEqual("01_abc123", sdid.to_strid())

    def test_str(self) -> None:
        sdid = StoredDataId("01", "abc123")
        self.assertEqual(sdid.to_strid(), str(sdid))
        self.assertEqual(sdid.to_strid(), repr(sdid))

    def test_from_strid(self) -> None:
        sdid = StoredDataId.from_strid("01_abc123")
        self.assertEqual(StoredDataId("01", "abc123"), sdid)


class Schema01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_schema_01_empty(self) -> None:
        path = Path(self.tempdir.name) / "file.bin"
        with path.open("wb") as f:
            f.write(b'')

        hash = hashlib.blake2b(b'', digest_size=16, person=b'arbox')
        self.assertEqual(
            StoredDataId("01", hash.digest().hex()),
            sdid_schema_01(path)
        )

    def test_schema_01_small(self) -> None:
        contents = b'hello, world!'
        path = Path(self.tempdir.name) / "file.bin"
        with path.open("wb") as f:
            f.write(contents)

        hash = hashlib.blake2b(contents, digest_size=16, person=b'arbox')
        self.assertEqual(
            StoredDataId("01", hash.digest().hex()),
            sdid_schema_01(path)
        )

    def test_schema_01_large(self) -> None:
        hash = hashlib.blake2b(digest_size=16, person=b'arbox')
        path = Path(self.tempdir.name) / "file.bin"
        with path.open("wb") as f:
            block = b'hello, world!'
            for i in range(81000): # more than 1 MB
                f.write(block)
                hash.update(block)

        self.assertEqual(
            StoredDataId("01", hash.digest().hex()),
            sdid_schema_01(path)
        )
