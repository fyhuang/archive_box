import unittest
import sqlite3
from datetime import datetime

from .processor_state import *


class ProcessorStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.ps = ProcessorState(self.conn)
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
