import sqlite3
import unittest
from typing import Optional, Tuple

from .synced_db import *
from .node_config import NodeConfig
from .protodb import ProtoTable
from . import test_pb2


class MockLog(object):
    def __init__(self):
        self.entries = []

    def add_entry(self, node_config, entity_name, entity_id, msg):
        self.entries.append((node_config, entity_name, entity_id, msg))


class SyncedDbIntegrationTests(unittest.TestCase):
    def make_table_and_db(self, msg_class, node_num: int) -> Tuple[sqlite3.Connection, ProtoTable, SyncedDb]:
        conn = sqlite3.connect(":memory:")

        pt = ProtoTable(conn, msg_class)
        pt.first_time_setup()

        db = SyncedDb(conn, NodeConfig(node_num, str(node_num)), [pt])
        db.first_time_setup()

        return (conn, pt, db)

    def test_sync_simple(self) -> None:
        conn1, pt1, db1 = self.make_table_and_db(test_pb2.Simple, 1)
        conn2, pt2, db2 = self.make_table_and_db(test_pb2.Simple, 2)

        msg = test_pb2.Simple()
        msg.id = "s0"
        msg.opt_string = "hello"
        msg.req_bool = False
        pt1.update(msg)
        self.assertEqual(msg, pt1.get("s0"))

        # sync new object
        self.assertEqual(None, pt2.get("s0"))
        db2.sync(conn1)
        self.assertEqual(pt1.get("s0"), pt2.get("s0"))

        # sync modified object
        msg.opt_string = "world"
        msg.req_bool = True
        pt2.update(msg)
        db1.sync(conn2)
        self.assertEqual(pt2.get("s0"), pt1.get("s0"))

        # sync deleted object
        # TODO(fyhuang)

    def test_sync_merge(self) -> None:
        conn1, pt1, db1 = self.make_table_and_db(test_pb2.MergeTest, 1)
        conn2, pt2, db2 = self.make_table_and_db(test_pb2.MergeTest, 2)

        msg = test_pb2.MergeTest()
        msg.id = "s0"
        msg.s_error = "1"
        msg.s_latest = "1"

        # no-op merge, since all fields are identical
        pt1.update(msg)
        pt2.update(msg)
        db1.sync(conn2)
        self.assertEqual(pt2.get("s0"), pt1.get("s0"))

        # merge latest
        msg.s_latest = "2"
        pt1.update(msg)
        msg.s_latest = "3"
        pt2.update(msg)
        db1.sync(conn2)
        self.assertEqual("3", pt1.getx("s0").s_latest)

        # merge error
        msg.s_error = "2"
        pt1.update(msg)
        msg.s_error = "3"
        pt2.update(msg)
        with self.assertRaises(RuntimeError):
            db1.sync(conn2)

    def test_sync_merge_lists(self) -> None:
        conn1, pt1, db1 = self.make_table_and_db(test_pb2.MergeTest, 1)
        conn2, pt2, db2 = self.make_table_and_db(test_pb2.MergeTest, 2)

        msg = test_pb2.MergeTest()
        msg.id = "s0"
        msg.r_i32_error[:] = [1, 2, 3]
        msg.r_i32_sunion[:] = [1, 2, 3]
        msg.r_i32_lunion[:] = [1, 2, 3]

        # no-op merge
        pt1.update(msg)
        pt2.update(msg)
        db1.sync(conn2)
        self.assertEqual(msg, pt1.get("s0"))

        # merge set union
        msg.r_i32_sunion[:] = [1, 2, 3]
        pt1.update(msg)
        msg.r_i32_sunion[:] = [1, 2, 4]
        pt2.update(msg)
        db1.sync(conn2)
        self.assertEqual(set([1, 2, 3, 4]), set(pt1.getx("s0").r_i32_sunion))

        # merge list union
        msg.r_i32_lunion[:] = [1, 2]
        pt1.update(msg)
        msg.r_i32_lunion[:] = [3, 4]
        pt2.update(msg)
        db1.sync(conn2)
        self.assertEqual([1, 2, 3, 4], pt1.getx("s0").r_i32_lunion)

        # merge error
        msg.r_i32_error[:] = [1, 2, 3]
        pt1.update(msg)
        msg.r_i32_error[:] = [1, 2, 4]
        pt2.update(msg)
        with self.assertRaises(RuntimeError):
            db1.sync(conn2)

    def test_sync_merge_maps(self) -> None:
        conn1, pt1, db1 = self.make_table_and_db(test_pb2.MergeTest, 1)
        conn2, pt2, db2 = self.make_table_and_db(test_pb2.MergeTest, 2)

        msg = test_pb2.MergeTest()
        msg.id = "s0"
        msg.m_si32_ul.update({"a": 1})

        # no-op merge
        pt1.update(msg)
        pt2.update(msg)
        db1.sync(conn2)
        self.assertEqual(msg, pt1.get("s0"))

        # merge union latest
        msg.m_si32_ul["a"] = 2
        msg.m_si32_ul["b"] = 1
        pt1.update(msg)

        msg.m_si32_ul.clear()
        msg.m_si32_ul["a"] = 3
        pt2.update(msg)

        db1.sync(conn2)
        self.assertEqual({"a": 3, "b": 1}, pt1.getx("s0").m_si32_ul)
