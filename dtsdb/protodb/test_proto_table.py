import sqlite3
import unittest

from .proto_table import *
from dtsdb import test_pb2


class ProtoTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")

    def test_no_id(self) -> None:
        with self.assertRaises(RuntimeError):
            st = ProtoTable(self.conn, test_pb2.NoId)

    def test_get_update_nested(self) -> None:
        st = ProtoTable(self.conn, test_pb2.Nested)
        st.first_time_setup()

        msg = test_pb2.Nested()
        msg.id = "s0"
        msg.selection = test_pb2.Nested.WORLD
        msg.inner.f1 = "f1"
        msg.inner.f2 = 32
        st.update(msg)

        stored = st.get("s0")
        self.assertEqual(msg, stored)

    def test_update_callback(self) -> None:
        entries = []
        def callback(id, contents):
            entries.append((id, contents))

        st = ProtoTable(self.conn, test_pb2.Simple)
        st.first_time_setup()
        st.add_callback(callback)

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

    def test_queryall(self) -> None:
        pt = ProtoTable(self.conn, test_pb2.Simple)
        pt.first_time_setup()

        msg1 = test_pb2.Simple()
        msg1.id = "m1"
        msg1.opt_string = "b"
        msg1.req_bool = True
        pt.update(msg1)

        msg2 = test_pb2.Simple()
        msg2.id = "m2"
        msg2.opt_string = "a"
        msg2.req_bool = False
        pt.update(msg2)

        self.assertEqual([msg1], pt.queryall(lambda m: m.req_bool))
        self.assertEqual([msg2, msg1],
                pt.queryall(lambda m: True, lambda m: m.opt_string))
        self.assertEqual([msg1, msg2],
                pt.queryall(lambda m: True, lambda m: m.opt_string, reverse=True))

