import sqlite3
import unittest
from typing import Optional

from .synced_db import *
from .node_config import NodeConfig
from . import test_pb2


def unwrap(optional: Optional[Any]) -> Any:
    if optional is None:
        raise RuntimeError("unwrap None")
    return optional


class MockLog(object):
    def __init__(self):
        self.entries = []

    def add_entry(self, node_config, entity_name, entity_id, msg):
        self.entries.append((node_config, entity_name, entity_id, msg))


class SyncedDbIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn1 = sqlite3.connect(":memory:")
        self.conn2 = sqlite3.connect(":memory:")

    def tearDown(self) -> None:
        self.conn1.close()
        self.conn2.close()

    def test_sync_simple(self) -> None:
        schemas = [test_pb2.Simple]
        db1 = SyncedDb(self.conn1, NodeConfig(1, ""), schemas)
        db2 = SyncedDb(self.conn2, NodeConfig(2, ""), schemas)
        db1.first_time_setup()
        db2.first_time_setup()

        msg = test_pb2.Simple()
        msg.id = "s0"
        msg.opt_string = "hello"
        msg.req_bool = False
        db1.get_table("Simple").update(msg)
        self.assertEqual(msg, db1.get_table("Simple").get("s0"))

        # sync new object
        self.assertEqual(None, db2.get_table("Simple").get("s0"))
        db2.sync(self.conn1)
        self.assertEqual(
            db1.get_table("Simple").get("s0"),
            db2.get_table("Simple").get("s0")
        )

        # sync modified object
        msg.opt_string = "world"
        msg.req_bool = True
        db2.get_table("Simple").update(msg)
        db1.sync(self.conn2)
        self.assertEqual(
            db2.get_table("Simple").get("s0"),
            db1.get_table("Simple").get("s0")
        )

        # sync deleted object
        # TODO(fyhuang)

    def test_sync_merge(self) -> None:
        schemas = [test_pb2.MergeTest]
        db1 = SyncedDb(self.conn1, NodeConfig(1, ""), schemas)
        db2 = SyncedDb(self.conn2, NodeConfig(2, ""), schemas)
        db1.first_time_setup()
        db2.first_time_setup()

        msg = test_pb2.MergeTest()
        msg.id = "s0"
        msg.s_error = "1"
        msg.s_latest = "1"

        # no-op merge, since all fields are identical
        db1.get_table("MergeTest").update(msg)
        db2.get_table("MergeTest").update(msg)
        db1.sync(self.conn2)
        self.assertEqual(
            db2.get_table("MergeTest").get("s0"),
            db1.get_table("MergeTest").get("s0")
        )

        # merge latest
        msg.s_latest = "2"
        db1.get_table("MergeTest").update(msg)
        msg.s_latest = "3"
        db2.get_table("MergeTest").update(msg)
        db1.sync(self.conn2)
        self.assertEqual("3", unwrap(db1.get_table("MergeTest").get("s0")).s_latest)

        # merge error
        msg.s_error = "2"
        db1.get_table("MergeTest").update(msg)
        msg.s_error = "3"
        db2.get_table("MergeTest").update(msg)
        with self.assertRaises(RuntimeError):
            db1.sync(self.conn2)

    def test_sync_merge_lists(self) -> None:
        schemas = [test_pb2.MergeTest]
        db1 = SyncedDb(self.conn1, NodeConfig(1, ""), schemas)
        db2 = SyncedDb(self.conn2, NodeConfig(2, ""), schemas)
        db1.first_time_setup()
        db2.first_time_setup()

        msg = test_pb2.MergeTest()
        msg.id = "s0"
        msg.r_i32_error[:] = [1, 2, 3]
        msg.r_i32_sunion[:] = [1, 2, 3]
        msg.r_i32_lunion[:] = [1, 2, 3]

        # no-op merge
        db1.get_table("MergeTest").update(msg)
        db2.get_table("MergeTest").update(msg)
        db1.sync(self.conn2)
        self.assertEqual(msg, db1.get_table("MergeTest").get("s0"))

        # merge set union
        msg.r_i32_sunion[:] = [1, 2, 3]
        db1.get_table("MergeTest").update(msg)
        msg.r_i32_sunion[:] = [1, 2, 4]
        db2.get_table("MergeTest").update(msg)
        db1.sync(self.conn2)
        self.assertEqual(set([1, 2, 3, 4]),
                set(db1.get_table("MergeTest").getx("s0").r_i32_sunion))

        # merge list union
        msg.r_i32_lunion[:] = [1, 2]
        db1.get_table("MergeTest").update(msg)
        msg.r_i32_lunion[:] = [3, 4]
        db2.get_table("MergeTest").update(msg)
        db1.sync(self.conn2)
        self.assertEqual([1, 2, 3, 4], db1.get_table("MergeTest").getx("s0").r_i32_lunion)

        # merge error
        msg.r_i32_error[:] = [1, 2, 3]
        db1.get_table("MergeTest").update(msg)
        msg.r_i32_error[:] = [1, 2, 4]
        db2.get_table("MergeTest").update(msg)
        with self.assertRaises(RuntimeError):
            db1.sync(self.conn2)

    def test_sync_merge_maps(self) -> None:
        schemas = [test_pb2.MergeTest]
        db1 = SyncedDb(self.conn1, NodeConfig(1, ""), schemas)
        db2 = SyncedDb(self.conn2, NodeConfig(2, ""), schemas)
        db1.first_time_setup()
        db2.first_time_setup()

        msg = test_pb2.MergeTest()
        msg.id = "s0"
        msg.m_si32_ul.update({"a": 1})

        # no-op merge
        db1.get_table("MergeTest").update(msg)
        db2.get_table("MergeTest").update(msg)
        db1.sync(self.conn2)
        self.assertEqual(msg, db1.get_table("MergeTest").get("s0"))

        # merge union latest
        msg.m_si32_ul["a"] = 2
        msg.m_si32_ul["b"] = 1
        db1.get_table("MergeTest").update(msg)

        msg.m_si32_ul.clear()
        msg.m_si32_ul["a"] = 3
        db2.get_table("MergeTest").update(msg)

        db1.sync(self.conn2)
        self.assertEqual({"a": 3, "b": 1}, db1.get_table("MergeTest").getx("s0").m_si32_ul)
