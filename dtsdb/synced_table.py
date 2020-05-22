import sqlite3
from typing import List, NamedTuple
from google.protobuf.message import Message
from google.protobuf.descriptor import Descriptor, FieldDescriptor

from . import schema_pb2 as pb2
from .log import Log


#class Column(NamedTuple):
#    cid: int
#    name: str
#    data_type: str
#    notnull: bool
#    default_value: str
#    primary_key: int


def _protobuf_to_sqlite_type(field_type):
    if field_type == FieldDescriptor.TYPE_BOOL:
        return "BOOLEAN"
    elif field_type == FieldDescriptor.TYPE_BYTES:
        return "BLOB"
    elif field_type in (FieldDescriptor.TYPE_DOUBLE, FieldDescriptor.TYPE_FLOAT):
        return "DOUBLE"
    elif field_type in (FieldDescriptor.TYPE_FIXED32,
            FieldDescriptor.TYPE_FIXED64,
            FieldDescriptor.TYPE_INT32,
            FieldDescriptor.TYPE_INT64,
            FieldDescriptor.TYPE_SFIXED32,
            FieldDescriptor.TYPE_SFIXED64,
            FieldDescriptor.TYPE_UINT32,
            FieldDescriptor.TYPE_UINT64):
        return "INTEGER"
    elif field_type in (FieldDescriptor.TYPE_ENUM, FieldDescriptor.TYPE_STRING):
        return "TEXT"
    else:
        raise RuntimeError("Unsupported field type {}".format(field_type))


class SyncedTable(object):
    def __init__(self, conn: sqlite3.Connection, msg_descriptor: Descriptor) -> None:
        self.conn = conn
        self.msg_descriptor = msg_descriptor
        self.entity_name = self.msg_descriptor.GetOptions().Extensions[pb2.table].name
        if self.entity_name == "":
            raise RuntimeError("No table name declared in proto schema")
        self.table_name = "m_" + self.entity_name

    def _columns(self) -> List[str]:
        id_field = None
        columns = []
        def recur_columns(descriptor, name_prefix):
            nonlocal id_field
            for field in descriptor.fields:
                if field.message_type is not None:
                    recur_columns(field.message_type, name_prefix + field.name + "__")
                    continue

                field_pkey = ""
                if field.GetOptions().Extensions[pb2.field].is_id:
                    if id_field is not None:
                        raise RuntimeError("Only one field may be the id field")
                    id_field = field
                    field_pkey = "PRIMARY KEY"

                field_notnull = ""
                if field.label == FieldDescriptor.LABEL_REQUIRED:
                    field_notnull = "NOT NULL"
                elif field.label == FieldDescriptor.LABEL_REPEATED:
                    raise NotImplementedError("repeated fields not implemented yet")

                field_type = _protobuf_to_sqlite_type(field.type)
                raw_column_def = "{name} {type} {notnull} {pkey}".format(
                    name=name_prefix + field.name,
                    type=field_type,
                    notnull=field_notnull,
                    pkey=field_pkey,
                )
                columns.append(" ".join(raw_column_def.split()))

        recur_columns(self.msg_descriptor, "")
        if id_field is None:
            raise RuntimeError("No ID field was defined")
        return columns

    def _get_create_table_sql(self) -> str:
        return 'CREATE TABLE IF NOT EXISTS {tname} ({columns})'.format(
            tname=self.table_name,
            columns=', '.join(self._columns())
        )

    def init_table(self) -> None:
        # throws exception if the db already contains a table whose schema doesn't match the one
        # implied by `msg_descriptor`
        create_table = self._get_create_table_sql()
        self.conn.execute(create_table)

    def update(self, entity_id: str, updated_msg: Message, log: Log) -> None:
        pass
