import sqlite3
from typing import Optional, List, Any, Callable

from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor

from . import log, schema_pb2
from .node_config import NodeConfig
from .protodb import proto_table, proto_util


class MessageMerger(object):
    """Merges "other_msg" into "our_msg" according to user-defined rules."""
    def __init__(self,
            create_msg: Callable,
            our_entry: log.Entry,
            their_entry: log.Entry,
            ) -> None:
        self.our_entry = our_entry
        self.their_entry = their_entry

        self.our_msg = create_msg()
        if our_entry.entity is not None:
            self.our_msg.ParseFromString(our_entry.entity)
        self.their_msg = create_msg()
        if their_entry.entity is not None:
            self.their_msg.ParseFromString(their_entry.entity)

        self.result_msg = create_msg()

    def _merge_primitive(self, strategy, our_pf, their_pf, result_pf):
        if strategy == "latest":
            if self.our_entry.timestamp >= self.their_entry.timestamp:
                result_pf.copy(our_pf)
            else:
                result_pf.copy(their_pf)
        else:
            raise RuntimeError("merge strategy {} doesn't apply to primitive fields".format(strategy))

    def _merge_list(self, strategy, our_pf, their_pf, result_pf):
        # TODO(fyhuang): also support plain latest?
        if strategy == "set_union":
            all_elements = set()
            all_elements.update(our_pf.get())
            all_elements.update(their_pf.get())
        elif strategy == "list_union":
            all_elements = []
            all_elements.extend(our_pf.get())
            all_elements.extend(their_pf.get())
        else:
            raise RuntimeError("merge strategy {} doesn't apply to repeated fields".format(strategy))

        del result_pf.get()[:]
        result_pf.get().extend(all_elements)

    def _merge_map_primitive(self, strategy, our_pf, their_pf, result_pf):
        if strategy == "union_latest":
            if self.our_entry.timestamp >= self.their_entry.timestamp:
                order = [their_pf, our_pf]
            else:
                order = [our_pf, their_pf]

            result_pf.get().clear()
            for pf in order:
                result_pf.get().update(pf.get())
        else:
            raise RuntimeError("merge strategy {} doesn't apply to map fields".format(strategy))

    def _merge_map_message(self, strategy, our_pf, their_pf, result_pf):
        if strategy == "union_latest":
            if self.our_entry.timestamp >= self.their_entry.timestamp:
                order = [their_pf, our_pf]
            else:
                order = [our_pf, their_pf]

            result_pf.get().clear()
            for pf in order:
                for key, value in pf.get().items():
                    result_pf.get()[key].CopyFrom(value)
        else:
            raise RuntimeError("merge strategy {} doesn't apply to map fields".format(strategy))

    def merge(self) -> Any:
        self.result_msg.CopyFrom(self.our_msg)

        # iterate through fields and check merge strategy
        for nf in proto_util.iter_nested_fields(self.our_msg.DESCRIPTOR):
            our_pf = proto_util.Pathfinder(self.our_msg, nf.name_path)
            their_pf = proto_util.Pathfinder(self.their_msg, nf.name_path)

            if our_pf.get() == their_pf.get():
                # no need to merge
                continue

            result_pf = proto_util.Pathfinder(self.result_msg, nf.name_path)
            strategy = nf.desc.GetOptions().Extensions[schema_pb2.field].merge

            # error out if strategy is "error"
            if strategy == "" or strategy == "error":
                raise RuntimeError("conflict detected: '{}' != '{}'".format(our_pf.get(), their_pf.get()))

            # check field type
            is_repeated = nf.desc.label == FieldDescriptor.LABEL_REPEATED
            if nf.map_value is not None:
                if nf.map_value.message_type is None:
                    self._merge_map_primitive(strategy, our_pf, their_pf, result_pf)
                else:
                    self._merge_map_message(strategy, our_pf, their_pf, result_pf)
            elif is_repeated:
                self._merge_list(strategy, our_pf, their_pf, result_pf)
            else:
                self._merge_primitive(strategy, our_pf, their_pf, result_pf)

        return self.result_msg


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
        merger = MessageMerger(table.new, our, other)
        return merger.merge()

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
