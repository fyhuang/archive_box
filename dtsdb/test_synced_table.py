import unittest

from .synced_table import *
from . import test_pb2

class SyncedTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")

    def test_columns(self) -> None:
        st = SyncedTable(self.conn, test_pb2.Simple.DESCRIPTOR) # type: ignore
        self.assertEqual(
            [
                "id TEXT NOT NULL PRIMARY KEY",
                "opt_string TEXT  ",
                "req_bool BOOLEAN NOT NULL ",
            ],
            st._columns()
        )
