import unittest

import sqlite3
import tempfile
import os.path
from datetime import datetime
from typing import List

from .log import *
from .node_config import NodeConfig
from .vector_clock import VectorClock

class LogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.timestamps: List[datetime] = []
        self.last_second = 0

    def next_ts(self) -> datetime:
        return self.timestamps.pop(0)

    def counter_ts(self) -> datetime:
        dt = datetime.fromtimestamp(self.last_second)
        self.last_second += 1
        return dt

    def test_first_time_setup_duplicate(self) -> None:
        log = Log(self.conn)
        log.first_time_setup()
        # performing setup multiple times should not result in error
        log.first_time_setup()

    def test_register_node_duplicate(self) -> None:
        log = Log(self.conn)
        log._register_node(NodeConfig(123, "my node"))
        log._register_node(NodeConfig(123, "my node again"))
        self.assertEqual(
            set([NodeConfig(123, "my node")]),
            set(log._get_known_nodes())
        )

    def test_oldest_node_ts(self) -> None:
        self.timestamps = [datetime.fromtimestamp(100), datetime.fromtimestamp(200)]
        log = Log(self.conn, self.next_ts)
        log.add_entry(NodeConfig(100, ""), "Entity", "e0", b'')
        self.assertEqual(datetime.fromtimestamp(100), log._oldest_node_ts())
        log.add_entry(NodeConfig(200, ""), "Entity", "e1", b'')
        self.assertEqual(datetime.fromtimestamp(100), log._oldest_node_ts())

    def test_newest_timestamp(self) -> None:
        self.timestamps = [datetime.fromtimestamp(200)]
        log = Log(self.conn, self.next_ts)
        log.add_entry(NodeConfig(1, ""), "Entity", "e0", b'')
        self.assertEqual(datetime.fromtimestamp(200), log._newest_timestamp())

    def test_advance_vclock(self) -> None:
        vc = VectorClock()
        log = Log(self.conn, self.counter_ts)
        self.assertEqual(VectorClock(), log._newest_vclock())

        log.add_entry(NodeConfig(1, ""), "Entity", "e0", b'')
        self.assertEqual(VectorClock({1:1}), log._newest_vclock())

        log.add_entry(NodeConfig(2, ""), "Entity", "e1", b'')
        self.assertEqual(VectorClock({1:1, 2:1}), log._newest_vclock())

        log.add_entry(NodeConfig(1, ""), "Entity", "e0", b'')
        self.assertEqual(VectorClock({1:2, 2:1}), log._newest_vclock())

    def test_get_entries_since(self) -> None:
        self.timestamps = [datetime.fromtimestamp(1), datetime.fromtimestamp(2), datetime.fromtimestamp(3)]
        log = Log(self.conn, self.next_ts)

        log.add_entry(NodeConfig(1, ""), "Entity", "e1", b'')
        log.add_entry(NodeConfig(2, ""), "Entity", "e2", b'')
        log.add_entry(NodeConfig(1, ""), "Entity", "e3", b'')

        all_entries = [
            Entry(datetime.fromtimestamp(1), "Entity", "e1", b'', VectorClock({1: 1})),
            Entry(datetime.fromtimestamp(2), "Entity", "e2", b'', VectorClock({1: 1, 2: 1})),
            Entry(datetime.fromtimestamp(3), "Entity", "e3", b'', VectorClock({1: 2, 2: 1})),
        ]
        self.assertEqual(all_entries, log._get_all_real_entries())

    def test_get_latest_entry_per_entity(self) -> None:
        self.timestamps = [datetime.fromtimestamp(1), datetime.fromtimestamp(2), datetime.fromtimestamp(3)]
        log = Log(self.conn, self.next_ts)
        log.add_entry(NodeConfig(1, ""), "Int", "i0", b'')
        log.add_entry(NodeConfig(2, ""), "Int", "i1", b'')
        log.add_entry(NodeConfig(1, ""), "Float", "f0", b'')
        self.assertEqual(
            {
                EntityKey("Int", "i0"): Entry(
                    datetime.fromtimestamp(1), "Int", "i0", b'', VectorClock({1:1})
                ),
                EntityKey("Int", "i1"): Entry(
                    datetime.fromtimestamp(2), "Int", "i1", b'', VectorClock({1:1, 2:1})
                ),
                EntityKey("Float", "f0"): Entry(
                    datetime.fromtimestamp(3), "Float", "f0", b'', VectorClock({1:2, 2:1})
                ),
            },
            log._get_latest_entry_per_entity()
        )

    def test_detect_changes_none(self) -> None:
        log1 = Log(self.conn, self.counter_ts)
        second_conn = sqlite3.connect(":memory:")
        log2 = Log(second_conn, self.counter_ts)

        log1.add_entry(NodeConfig(1, ""), "Int", "i0", b'')
        log1.add_entry(NodeConfig(2, ""), "Int", "i1", b'')

        # everything in log1 is after log2
        self.assertEqual([], log1.detect_changes(log2))

        # both logs are equal
        log2.add_entry(NodeConfig(1, ""), "Int", "i0", b'')
        log2.add_entry(NodeConfig(2, ""), "Int", "i1", b'')
        self.assertEqual([], log1.detect_changes(log2))

    def test_detect_changes(self) -> None:
        log1 = Log(self.conn, self.counter_ts)
        second_conn = sqlite3.connect(":memory:")
        log2 = Log(second_conn, self.counter_ts)

        log1.add_entry(NodeConfig(1, ""), "Int", "i0", b'a')
        log1.add_entry(NodeConfig(2, ""), "Int", "i1", b'1')
        log2.add_entry(NodeConfig(3, ""), "Int", "i0", b'b')

        # i1 is new in log2; i0 has a conflict
        self.assertEqual(
            set([
                Change("conflict", "Int", "i0", b'a'),
                Change("modified", "Int", "i1", b'1'),
            ]),
            set(log2.detect_changes(log1))
        )

    def test_merge_from(self) -> None:
        self.timestamps = [datetime.fromtimestamp(1), datetime.fromtimestamp(2), datetime.fromtimestamp(3), datetime.fromtimestamp(4)]
        log1 = Log(self.conn, self.next_ts)
        second_conn = sqlite3.connect(":memory:")
        log2 = Log(second_conn, self.next_ts)

        log1.add_entry(NodeConfig(1, ""), "Int", "i0", b'a')
        log1.add_entry(NodeConfig(1, ""), "Int", "i1", b'1')
        log2.add_entry(NodeConfig(2, ""), "Int", "i0", b'b')

        log2.merge_from(log1)
        self.assertEqual(
            [
                Entry(datetime.fromtimestamp(1), "Int", "i0", b'a', VectorClock({1: 1})),
                Entry(datetime.fromtimestamp(2), "Int", "i1", b'1', VectorClock({1: 2})),
                Entry(datetime.fromtimestamp(3), "Int", "i0", b'b', VectorClock({2: 1})),
            ],
            log2._get_all_real_entries()
        )

        self.assertEqual(VectorClock({1: 2, 2: 1}), log2._newest_vclock())
        self.assertEqual(datetime.fromtimestamp(4), log2._newest_timestamp())
