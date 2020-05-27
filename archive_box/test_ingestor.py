import unittest
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict

from .ingestor import *
from .storage.stored_data import StoredDataId, file_to_sdid
from . import manager as mgr


class MockStorage(object):
    def __init__(self, cid) -> None:
        self.cid = cid
        self.uploads: List[Tuple[StoredDataId, Path]] = []

    def upload(self, sdid: StoredDataId, src_file: Path) -> None:
        self.uploads.append((sdid, src_file))


class MockManager(object):
    def __init__(self) -> None:
        self.storages: Dict[str, MockStorage] = {}

    def col(self, cid: str) -> mgr.Collection:
        self.storages.setdefault(cid, MockStorage(cid))
        return mgr.Collection(None, None, self.storages[cid]) # type: ignore


class IngestorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.manager = MockManager()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_scan_upload(self) -> None:
        ingestor = Ingestor(self.tempdir.name, self.manager) # type: ignore

        # empty dir should do nothing
        ingestor.scan_inbox()
        self.assertEqual(0, len(self.manager.storages))

        # one file with no target collection
        filepath = Path(self.tempdir.name) / "temp.txt"
        with filepath.open("w") as f:
            f.write("hello")
        sdid = file_to_sdid(filepath)
        ingestor.scan_inbox()
        self.assertEqual([sdid], list(ingestor.get_waiting().keys()))
        self.assertEqual(0, len(self.manager.storages))

        # set the target collection and scan again
        ingestor.set_target(sdid, "abc123")
        ingestor.scan_inbox()
        self.assertEqual(0, len(ingestor.get_waiting().keys()))
        self.assertEqual(sdid, self.manager.storages["abc123"].uploads[0][0])
