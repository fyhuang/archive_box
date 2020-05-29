import unittest
import sqlite3
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict

from .scanner import *
from .scanner_state import ScannerState
from archive_box.sdid import StoredDataId, file_to_sdid


class MockStorage(object):
    def __init__(self) -> None:
        self.uploads: List[Tuple[StoredDataId, Path]] = []

    def upload(self, sdid: StoredDataId, src_file: Path) -> None:
        self.uploads.append((sdid, src_file))


class ScannerWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.storage = MockStorage()
        self.conn = sqlite3.connect(":memory:")
        self.state = ScannerState(self.conn, self.tempdir.name)
        self.state.first_time_setup()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_basic(self) -> None:
        sw = ScannerWorker(self.tempdir.name, self.state, self.storage) # type: ignore
        sw.scan_inbox()
        self.assertEqual([], sw.to_ingest)

        filepath = Path(self.tempdir.name) / "temp.txt"
        with filepath.open("w") as f:
            f.write("hello")
        sdid = file_to_sdid(filepath)

        # one file
        sw.scan_inbox()
        self.assertEqual([filepath], sw.to_ingest)

        # ingest
        sw.ingest_all()
        self.assertEqual(
            [(sdid, filepath)],
            self.storage.uploads
        )

        # doesn't upload again
        sw.scan_inbox()
        sw.ingest_all()
        self.assertEqual(1, len(self.storage.uploads))
