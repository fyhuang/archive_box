import unittest
import sqlite3
from pathlib import Path

from archive_box.sdid import StoredDataId

from .scanner_state import *


class ScannerStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.ss = ScannerState(self.conn, Path("inbox"))
        self.ss.first_time_setup()

    def test_basic(self) -> None:
        filepath = Path("inbox") / "folder" / "test1.txt"
        self.assertFalse(self.ss.is_already_scanned(filepath))

        sdid = StoredDataId("01", "abc123")
        self.ss.record_scanned_file(filepath, sdid)
        self.assertTrue(self.ss.is_already_scanned(filepath))

        self.assertEqual([
            ScannedFile(Path("folder/test1.txt"), sdid),
        ], self.ss.get_all_scanned())

    def test_delete(self) -> None:
        filepath = Path("inbox") / "folder" / "test1.txt"
        sdid = StoredDataId("01", "abc123")
        self.ss.record_scanned_file(filepath, sdid)
        self.assertTrue(self.ss.is_already_scanned(filepath))

        self.ss.delete_scanned_file(sdid)
        self.assertFalse(self.ss.is_already_scanned(filepath))
