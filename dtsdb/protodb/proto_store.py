import sqlite3
from typing import Any, Dict, List, NamedTuple

from google.protobuf.descriptor import Descriptor, FieldDescriptor

from dtsdb


class NestedFieldDesc(NamedTuple):
    name_path: NamePath
    container_type: str # one_message, repeated_message, repeated_primitive, map


def _create_subtables(conn: sqlite3.Connection, root_desc: Descriptor):
    """Partition the fields and nested messages of a message amongst subtables."""
    message_tables = {}

    def recur(desc: Descriptor,
              path: path_pb2.Path):
        this_message_fields = []

        for field in desc.fields:
            repeated = field.label == FieldDescriptor.LABEL_REPEATED
            if field.message_type is None and not repeated:
                # just a regular field
                this_message_fields.append(field.name)
                continue

            if field.message_type is not None:
                pass
            elif repeated:
                # primitive repeated
                nested_subtable = ProtoSubtable("INT", _primitive_field(field.type))
            else:
                raise RuntimeError("unexpected branch")

        return ProtoSubtable("INT", this_message_fields)

    subtables[SubtableLink([], "one_message")] = recur(root_desc, [])
    return result


class ProtoStore(object):
    """A document store that uses a protobuf message as its schema. Uses a collection of subtables to represent the fields and sub-messages."""
    def __init__(self, conn: sqlite3.Connection, msg_class: Any) -> None:
        self.conn = conn
        self.msg_class = msg_class
        self.subtables = _create_subtables(conn, msg_class.DESCRIPTOR)
