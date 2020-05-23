import sqlite3
from typing import Any, List, NamedTuple
from google.protobuf.message import Message
from google.protobuf.descriptor import Descriptor, FieldDescriptor

from . import schema_pb2 as pb2
from .node_config import NodeConfig
from .log import Log


class ColumnDef(NamedTuple):
    name: str
    data_type: str
    required: bool
    primary_key: bool

    def to_sqlite_schema(self) -> str:
        col_notnull = ""
        if self.required:
            col_notnull = "NOT NULL"

        col_pkey = ""
        if self.primary_key:
            col_pkey = "PRIMARY KEY"

        raw_column_def = "{name} {type} {notnull} {pkey}".format(
            name=self.name,
            type=self.data_type,
            notnull=col_notnull,
            pkey=col_pkey,
        )
        return " ".join(raw_column_def.split())


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


def _is_id_field(field_desc):
    return field_desc.GetOptions().Extensions[pb2.field].is_id



class SyncedTable(object):
    def __init__(self, conn: sqlite3.Connection, msg_class: Any) -> None:
        self.conn = conn
        self.msg_class = msg_class
        self.msg_descriptor = msg_class.DESCRIPTOR

        self.entity_name = self.msg_descriptor.GetOptions().Extensions[pb2.table].name
        if self.entity_name == "":
            raise RuntimeError("No table name declared in proto schema")
        self.table_name = "m_" + self.entity_name
        self._parse_schema()

    def _parse_schema(self):
        id_field_name = None
        columns = []
        def recur_columns(descriptor, name_prefix):
            nonlocal id_field_name
            for field in descriptor.fields:
                if field.message_type is not None:
                    recur_columns(field.message_type, name_prefix + field.name + "__")
                    continue

                is_id = False
                if _is_id_field(field):
                    if id_field_name is not None:
                        raise RuntimeError("Only one field may be the id field")
                    id_field_name = name_prefix + field.name
                    is_id = True

                is_required = False
                if field.label == FieldDescriptor.LABEL_REQUIRED:
                    is_required = True
                elif field.label == FieldDescriptor.LABEL_REPEATED:
                    raise NotImplementedError("repeated fields not implemented yet")

                field_type = _protobuf_to_sqlite_type(field.type)
                columns.append(ColumnDef(name_prefix + field.name, field_type, is_required, is_id))

        recur_columns(self.msg_descriptor, "")
        if id_field_name is None:
            raise RuntimeError("No ID field was defined")

        self.columns = columns
        self.columns_by_name = {c.name: c for c in columns}
        self.id_field = id_field_name

    def _get_create_table_sql(self) -> str:
        return 'CREATE TABLE IF NOT EXISTS {tname} ({columns})'.format(
            tname=self.table_name,
            columns=', '.join([c.to_sqlite_schema() for c in self.columns])
        )

    def init_table(self) -> None:
        # throws exception if the db already contains a table whose schema doesn't match the one
        # implied by `msg_descriptor`
        create_table = self._get_create_table_sql()
        self.conn.execute(create_table)

        code_schema = create_table.replace("IF NOT EXISTS ", "")
        c = self.conn.cursor()
        c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (self.table_name,))
        existing_schema = c.fetchone()[0]
        if existing_schema != code_schema:
            #print("Schemas don't match:\n(database) {}\n(code) {}".format(
            #    existing_schema, code_schema))
            raise RuntimeError("Table in DB doesn't match declared schema")

    def get(self, id: str) -> Message:
        c = self.conn.cursor()
        row = c.execute("SELECT * FROM {} WHERE {}=?".format(self.table_name, self.id_field), (id,)).fetchone()

        msg = self.msg_class()

    def update(self, updated_msg: Message, node_config: NodeConfig, log: Log) -> None:
        id_value = None
        column_names = []
        values_list = []
        def recur_fields(message: Message, name_prefix):
            nonlocal id_value
            for field_desc, field_val in message.ListFields():
                if field_desc.message_type is not None:
                    recur_fields(field_val, name_prefix + field_desc.name + "__")
                    continue
                column_name = name_prefix + field_desc.name
                column_names.append(column_name)
                values_list.append(field_val)

                if _is_id_field(field_desc):
                    id_value = field_val

        recur_fields(updated_msg, "")
        query = "INSERT OR REPLACE INTO {} ({}) VALUES({})".format(
            self.table_name,
            ', '.join(column_names),
            ', '.join(['?'] * len(column_names)),
        )

        with self.conn:
            self.conn.execute(query, tuple(values_list))
        assert id_value is not None
        log.add_entry(node_config, self.entity_name, id_value, updated_msg.SerializeToString())
