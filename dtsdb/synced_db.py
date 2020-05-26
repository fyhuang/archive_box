import sqlite3
from typing import Optional, List, Any, Callable

from google.protobuf.message import Message

from . import log, schema_pb2
from .protodb import proto_table
from .node_config import NodeConfig


class SyncedDb(object):
    """A database which is automatically synced"""
    def __init__(self,
            conn: sqlite3.Connection,
            node_config: NodeConfig,
            schemas: List[Any],
            ) -> None:
        self.node_config = node_config
        self.log = log.Log(conn)
        self.tables = {}
        for s in schemas:
            name = proto_table.entity_name(s)
            pt = proto_table.ProtoTable(conn, s, self._update_cb(name))
            self.tables[name] = pt

    def _update_cb(self, entity_name) -> Callable[[str, Optional[bytes]], Any]:
        def cb(entity_id, serialized):
            self.log.add_entry(
                self.node_config,
                entity_name,
                entity_id,
                serialized
            )
        return cb

    def _merge_message(self, our: log.Entry, other: log.Entry) -> Message:
        table = self.tables[our.entity_name]
        our_msg = table.new()
        if our.entity is not None:
            our_msg.ParseFromString(our.entity)
        other_msg = table.new()
        if other.entity is not None:
            other_msg.ParseFromString(other.entity)

        # iterate through fields and check merge strategy
        for mf in proto_table.iter_fields(table.msg_descriptor):
            our_pf = proto_table.Pathfinder(our_msg, mf.name_path)
            other_pf = proto_table.Pathfinder(other_msg, mf.name_path)

            if our_pf.get() == other_pf.get():
                # no need to merge
                continue

            # check merge strategy
            strategy = mf.field_desc.GetOptions().Extensions[schema_pb2.field].merge
            if strategy == "" or strategy == "error":
                raise RuntimeError("conflict deteted: '{}' != '{}'".format(our_pf.get(), other_pf.get()))
            elif strategy == "latest":
                if our.timestamp < other.timestamp:
                    our_pf.set(other_pf.get())

        return our_msg

    def get_table(self, name: str) -> proto_table.ProtoTable:
        return self.tables[name]

    def sync(self, other_conn: sqlite3.Connection) -> None:
        other_log = log.Log(other_conn)
        changes = self.log.detect_changes(other_log)
        for c in changes:
            table = self.tables[c.entity_name]
            if c.type == "conflict":
                our_newest = self.log.get_newest_entry(c.entity_name, c.entity_id)
                other_newest = other_log.get_newest_entry(c.entity_name, c.entity_id)
                merged_msg = self._merge_message(our_newest, other_newest)
                # TODO(fyhuang): the vector clock recorded here is wrong (not merged)
                table.update(merged_msg, call_cb=True)
            elif c.entity is None:
                table.delete(c.entity_id, call_cb=False)
            else:
                entity = table.msg_class()
                entity.ParseFromString(c.entity)
                table.update(entity, call_cb=False)

        # now that all changes are applied, merge the logs
        self.log.merge_from(other_log)
