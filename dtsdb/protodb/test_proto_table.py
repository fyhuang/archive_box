import unittest

from .proto_table import *
from . import test_pb2


class ProtoTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")

    def test_no_table_name(self) -> None:
        with self.assertRaises(RuntimeError):
            st = ProtoTable(self.conn, test_pb2.NoTableName)

    def test_no_id(self) -> None:
        with self.assertRaises(RuntimeError):
            st = ProtoTable(self.conn, test_pb2.NoId)

    def test_columns_simple(self) -> None:
        st = ProtoTable(self.conn, test_pb2.Simple)
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
        st = ProtoTable(self.conn, test_pb2.Nested)
        self.assertEqual([
            ColumnDef("id", "TEXT", True, True),
            ColumnDef("selection", "TEXT", False, False),
            ColumnDef("inner__f1", "TEXT", False, False),
            ColumnDef("inner__f2", "INTEGER", True, False),
        ], st.columns)

    def test_create_table_simple(self) -> None:
        st = ProtoTable(self.conn, test_pb2.Simple)
        self.assertEqual(
            'CREATE TABLE IF NOT EXISTS m_Simple (id TEXT NOT NULL PRIMARY KEY, opt_string TEXT, req_bool BOOLEAN NOT NULL)',
            st._get_create_table_sql()
        )

    def test_wrong_schema_throws(self) -> None:
        # create a conflicting version of the table
        self.conn.execute('CREATE TABLE m_Simple (id TEXT NOT NULL PRIMARY KEY, opt_string INTEGER, req_bool BOOLEAN)')
        with self.assertRaises(RuntimeError):
            st = ProtoTable(self.conn, test_pb2.Simple)

    def test_update_callback(self) -> None:
        entries = []
        def callback(id, contents):
            entries.append((id, contents))

        st = ProtoTable(self.conn, test_pb2.Simple, callback)

        msg = test_pb2.Simple()
        msg.id = "s0"
        msg.opt_string = "str1"
        msg.req_bool = True
        st.update(msg)

        stored = st.get("s0")
        self.assertEqual(msg, stored)
        self.assertEqual(
            ("s0", msg.SerializeToString()),
            entries[0]
        )

        # make sure callback can be disabled
        st.update(msg, False)
        self.assertEqual(1, len(entries))

    def test_get_update_nested(self) -> None:
        st = ProtoTable(self.conn, test_pb2.Nested)

        msg = test_pb2.Nested()
        msg.id = "s0"
        msg.selection = test_pb2.Nested.WORLD
        msg.inner.f1 = "f1"
        msg.inner.f2 = 32
        st.update(msg)

        stored = st.get("s0")
        self.assertEqual(msg, stored)
