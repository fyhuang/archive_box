import unittest
import os
import time
import threading
import tempfile
import sqlite3
from datetime import datetime

from .processor_state import *


class ProcessorStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.cv = threading.Condition()
        self.ps = ProcessorState(self.conn, self.cv)
        self.ps.first_time_setup()

    def test_empty(self) -> None:
        self.assertEqual(None, self.ps.peek_next_item())
        self.assertEqual(0, self.ps.get_queue_size())

    def test_add_one(self) -> None:
        self.ps.add_work_item("doc1", "upload", datetime.fromtimestamp(100))
        self.assertEqual(1, self.ps.get_queue_size())
        wi = WorkItem(datetime.fromtimestamp(100), "doc1", "upload")
        self.assertEqual(wi, self.ps.peek_next_item())
        self.assertEqual([wi], self.ps.get_items_for_doc("doc1"))

    def test_queue_order(self) -> None:
        self.ps.add_work_item("doc1", "upload", datetime.fromtimestamp(100))
        self.ps.add_work_item("doc2", "upload", datetime.fromtimestamp(50))
        item = self.ps.peek_next_item()
        assert item is not None
        self.assertEqual(50.0, item.timestamp.timestamp())

    def test_pop(self) -> None:
        self.ps.add_work_item("doc1", "upload", datetime.fromtimestamp(100))
        self.ps.add_work_item("doc2", "upload", datetime.fromtimestamp(50))
        self.assertEqual(2, self.ps.get_queue_size())

        self.ps.pop_next_item()
        self.assertEqual(1, self.ps.get_queue_size())
        item = self.ps.peek_next_item()
        assert item is not None
        self.assertEqual(100.0, item.timestamp.timestamp())

    def test_wait(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_name = os.path.join(tempdir, "test.db")
            ps1 = ProcessorState(sqlite3.connect(db_name), self.cv)
            ps1.first_time_setup()

            def unblock():
                ps2 = ProcessorState(sqlite3.connect(db_name), self.cv)
                time.sleep(0.5)
                ps2.add_work_item("doc1", "upload")
            threading.Thread(target=unblock).start()

            ps1.wait_for_work()
