import unittest

from .synced_table import *
from . import test_pb2

class SyncedTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")

    def test_no_table_name(self) -> None:
        with self.assertRaises(RuntimeError):
            st = SyncedTable(self.conn, test_pb2.NoTableName.DESCRIPTOR)

    def test_no_id(self) -> None:
        with self.assertRaises(RuntimeError):
            st = SyncedTable(self.conn, test_pb2.NoId.DESCRIPTOR)

    def test_columns_simple(self) -> None:
        st = SyncedTable(self.conn, test_pb2.Simple.DESCRIPTOR)
        self.assertEqual([
            ColumnDef("id", "TEXT", True, True),
            ColumnDef("opt_string", "TEXT", False, False),
            ColumnDef("req_bool", "BOOLEAN", True, False),
        ], st.columns)

        self.assertEqual([
            "id TEXT NOT NULL PRIMARY KEY",
            "opt_string TEXT",
            "req_bool BOOLEAN NOT NULL",
        ], [c.to_sqlite_schema() for c in st.columns])

    def test_columns_nested(self) -> None:
        st = SyncedTable(self.conn, test_pb2.Nested.DESCRIPTOR)
        self.assertEqual([
            ColumnDef("id", "TEXT", True, True),
            ColumnDef("selection", "TEXT", False, False),
            ColumnDef("inner__f1", "TEXT", False, False),
            ColumnDef("inner__f2", "INTEGER", True, False),
        ], st.columns)

    def test_create_table_simple(self) -> None:
        st = SyncedTable(self.conn, test_pb2.Simple.DESCRIPTOR)
        self.assertEqual(
            'CREATE TABLE IF NOT EXISTS m_Simple (id TEXT NOT NULL PRIMARY KEY, opt_string TEXT, req_bool BOOLEAN NOT NULL)',
            st._get_create_table_sql()
        )

    def test_init_table_throws(self) -> None:
        # create a conflicting version of the table
        self.conn.execute('CREATE TABLE m_Simple (id TEXT NOT NULL PRIMARY KEY, opt_string INTEGER, req_bool BOOLEAN)')
        st = SyncedTable(self.conn, test_pb2.Simple.DESCRIPTOR)
        with self.assertRaises(RuntimeError):
            st.init_table()

    def test_update(self) -> None:
        st = SyncedTable(self.conn, test_pb2.Simple.DESCRIPTOR)
        st.init_table()

        msg = test_pb2.Simple()
        msg.id = "s0"
        msg.opt_string = "str1"
        msg.req_bool = True
        st.update(msg, None) # type: ignore

