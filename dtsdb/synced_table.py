import collections
import sqlite3
from typing import Any, Optional, List, NamedTuple, Generator

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


class MsgField(NamedTuple):
    field_name: str
    field_desc: FieldDescriptor
    id_field: bool
    db_column_name: str
    name_path: List[str]
    proto_value: Optional[Any]

    def to_sqlite_value(self):
        if self.field_desc.type == FieldDescriptor.TYPE_ENUM:
            enum_desc = self.field_desc.enum_type
            return enum_desc.values_by_number[self.proto_value].name
        else:
            return self.proto_value

    def from_sqlite_value(self, val) -> Any:
        if self.field_desc.type == FieldDescriptor.TYPE_ENUM:
            enum_desc = self.field_desc.enum_type
            return enum_desc.values_by_name[val].number
        else:
            return val


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

    def _iter_fields(self, msg: Optional[Message] = None) -> Generator[MsgField, None, None]:
        def recur(descriptor, msg, name_path_prefix, col_name_prefix):
            values_by_fnum = collections.defaultdict(lambda: None)
            if msg is not None:
                values_by_fnum.update({fd.number: value for fd, value in msg.ListFields()})

            for field in descriptor.fields:
                field_value = values_by_fnum[field.number]
                if field.message_type is not None:
                    yield from recur(
                        field.message_type,
                        field_value,
                        name_path_prefix + [field.name],
                        col_name_prefix + field.name + "__"
                    )
                    continue

                is_id = False
                if _is_id_field(field):
                    is_id = True

                yield MsgField(
                    field.name,
                    field,
                    is_id,
                    col_name_prefix + field.name,
                    name_path_prefix + [field.name],
                    field_value
                )

        yield from recur(self.msg_descriptor, msg, [], "")

    def _parse_schema(self):
        self.msg_fields_by_col = {}
        id_field_name = None
        columns = []
        for mf in self._iter_fields():
            if mf.id_field:
                if id_field_name is not None:
                    raise RuntimeError("Only one field may be the id field")
                id_field_name = mf.field_name

            is_required = False
            if mf.field_desc.label == FieldDescriptor.LABEL_REQUIRED:
                is_required = True
            elif mf.field_desc.label == FieldDescriptor.LABEL_REPEATED:
                raise NotImplementedError("repeated fields not implemented yet")

            field_type = _protobuf_to_sqlite_type(mf.field_desc.type)
            columns.append(ColumnDef(mf.db_column_name, field_type, is_required, mf.id_field))
            self.msg_fields_by_col[mf.db_column_name] = mf

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
        column_names = [col.name for col in self.columns]
        row = c.execute("SELECT {} FROM {} WHERE {}=?".format(
            ",".join(column_names),
            self.table_name,
            self.id_field
        ), (id,)).fetchone()

        msg = self.msg_class()
        for i, column in enumerate(self.columns):
            mf = self.msg_fields_by_col[column.name]
            container = msg
            for name in mf.name_path[:-1]:
                container = getattr(container, name)
            setattr(container, mf.name_path[-1], mf.from_sqlite_value(row[i]))

        return msg

    def update(self, updated_msg: Message, node_config: NodeConfig, log: Log) -> None:
        id_value = None
        column_names = []
        values_list = []
        for mf in self._iter_fields(updated_msg):
            column_names.append(mf.db_column_name)
            values_list.append(mf.to_sqlite_value())
            if mf.id_field:
                id_value = mf.to_sqlite_value()

        query = "INSERT OR REPLACE INTO {} ({}) VALUES({})".format(
            self.table_name,
            ', '.join(column_names),
            ', '.join(['?'] * len(column_names)),
        )

        assert id_value is not None
        with self.conn:
            self.conn.execute(query, tuple(values_list))
        log.add_entry(node_config, self.entity_name, id_value, updated_msg.SerializeToString())
