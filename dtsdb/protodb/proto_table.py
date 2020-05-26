import collections
import sqlite3
from typing import Any, Optional, Tuple, List, NamedTuple, Generator, Callable

from google.protobuf.message import Message
from google.protobuf.descriptor import Descriptor, FieldDescriptor

from dtsdb import sqlite_util
from .proto_subfield_table import ProtoSubfieldTable


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
    return field_desc.name == "id"


class Pathfinder(object):
    def __init__(self, msg: Message, name_path: List[str]):
        self.msg = msg
        self.name_path = name_path

        self.container = msg
        for name in name_path[:-1]:
            self.container = getattr(self.container, name)

    def get(self) -> Any:
        return getattr(self.container, self.name_path[-1])

    def set(self, value: Any) -> None:
        setattr(self.container, self.name_path[-1], value)


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

    is_repeated: bool
    is_map: bool

    def to_sqlite_value(self, val) -> Any:
        if self.is_repeated or self.is_map:
            raise RuntimeError("not supported")

        if self.field_desc.type == FieldDescriptor.TYPE_ENUM:
            enum_desc = self.field_desc.enum_type
            return enum_desc.values_by_number[val].name
        else:
            return val

    def from_sqlite_value(self, val) -> Any:
        if self.is_repeated or self.is_map:
            raise RuntimeError("not supported")

        if self.field_desc.type == FieldDescriptor.TYPE_ENUM:
            enum_desc = self.field_desc.enum_type
            return enum_desc.values_by_name[val].number
        else:
            return val


def entity_name(msg_class) -> str:
    return msg_class.DESCRIPTOR.name


def iter_fields(msg_descriptor: Descriptor) -> Generator[MsgField, None, None]:
    def recur(descriptor: Descriptor,
            name_path_prefix: List[str],
            col_name_prefix: str):

        for field in descriptor.fields:
            if field.name.startswith("_"):
                raise RuntimeError("Field names starting with \"_\" are reserved")
            if "__" in field.name:
                raise RuntimeError("Field names containing \"__\" are reserved")

            if field.message_type is not None:
                if field.message_type.GetOptions().map_entry:
                    # this field is actually a map<>
                    raise NotImplementedError("map not implemented")
                else:
                    if field.label != FieldDescriptor.LABEL_REQUIRED:
                        raise RuntimeError("Nested message fields must be required")
                    yield from recur(
                        field.message_type,
                        name_path_prefix + [field.name],
                        col_name_prefix + field.name + "__"
                    )
                    continue

            is_id = False
            if _is_id_field(field):
                is_id = True

            is_repeated = False
            if field.label == FieldDescriptor.LABEL_REPEATED:
                is_repeated = True

            yield MsgField(
                field_name=field.name,
                field_desc=field,
                id_field=is_id,
                db_column_name=col_name_prefix + field.name,
                name_path=name_path_prefix + [field.name],
                is_repeated=is_repeated,
                is_map=False,
            )

    yield from recur(msg_descriptor, [], "")


class ProtoTable(object):
    def __init__(self,
            conn: sqlite3.Connection,
            msg_class: Any,
            update_cb: Optional[Callable[[str, Optional[bytes]], Any]] = None,
            ) -> None:
        self.conn = conn
        self.msg_class = msg_class
        self.msg_descriptor = msg_class.DESCRIPTOR
        self.update_cb = update_cb

        self.entity_name = entity_name(msg_class)
        if self.entity_name == "":
            raise RuntimeError("No table name declared in proto schema")
        self.table_name = "m_" + self.entity_name
        self._parse_schema()
        self.columns_by_name = {c.name: c for c in self.columns}

        self._init_table()

    def _parse_schema(self) -> None:
        self.msg_fields_by_col = {}
        id_field_name = None
        columns = []
        subfield_tables = {}
        for mf in iter_fields(self.msg_descriptor):
            if mf.id_field:
                if id_field_name is not None:
                    raise RuntimeError("Only one field may be the id field")
                if mf.field_desc.type != FieldDescriptor.TYPE_STRING:
                    raise RuntimeError("ID field must be string type")
                id_field_name = mf.field_name

            is_required = False
            if mf.field_desc.label == FieldDescriptor.LABEL_REQUIRED:
                is_required = True

            if not mf.is_repeated and not mf.is_map:
                field_type = _protobuf_to_sqlite_type(mf.field_desc.type)
                columns.append(ColumnDef(mf.db_column_name, field_type, is_required, mf.id_field))
                self.msg_fields_by_col[mf.db_column_name] = mf
            else:
                if mf.is_repeated:
                    key_type = "INT"
                    value_type = _protobuf_to_sqlite_type(mf.field_desc.type)
                else:
                    key_type = _protobuf_to_sqlite_type(mf.field_desc.message_type.fields_by_number[1].type)
                    value_type = _protobuf_to_sqlite_type(mf.field_desc.message_type.fields_by_number[2].type)

                subfield_tables[mf.db_column_name] = ProtoSubfieldTable(
                    self.conn,
                    self.table_name,
                    mf.db_column_name,
                    key_type,
                    value_type,
                )

        if id_field_name is None:
            raise RuntimeError("No ID field was defined")

        self.columns = columns
        self.id_field = id_field_name
        self.subfield_tables = subfield_tables

    def _get_create_table_sql(self) -> str:
        return 'CREATE TABLE IF NOT EXISTS {tname} ({columns})'.format(
            tname=self.table_name,
            columns=', '.join([c.to_sqlite_schema() for c in self.columns])
        )

    def _init_table(self) -> None:
        # throws exception if the db already contains a table whose schema doesn't match the one
        # implied by `msg_descriptor`
        create_table = self._get_create_table_sql()
        sqlite_util.ensure_table_matches(self.conn, create_table)

    def get(self, id: str) -> Optional[Any]:
        c = self.conn.cursor()
        column_names = [col.name for col in self.columns]
        row = c.execute("SELECT {} FROM {} WHERE {}=?".format(
            ",".join(column_names),
            self.table_name,
            self.id_field
        ), (id,)).fetchone()

        if row is None:
            return None

        msg = self.msg_class()
        for i, column in enumerate(self.columns):
            mf = self.msg_fields_by_col[column.name]
            Pathfinder(msg, mf.name_path).set(mf.from_sqlite_value(row[i]))

        return msg

    def new(self) -> Any:
        return self.msg_class()

    def update(self, updated_msg: Message, call_cb: bool = True) -> None:
        if not updated_msg.IsInitialized():
            raise RuntimeError("updated_msg must be initialized")

        id_value = None
        column_names = []
        values_list = []
        for _, mf in self.msg_fields_by_col.items():
            column_names.append(mf.db_column_name)
            value = mf.to_sqlite_value(Pathfinder(updated_msg, mf.name_path).get())
            values_list.append(value)
            if mf.id_field:
                id_value = value

        query = "INSERT OR REPLACE INTO {} ({}) VALUES({})".format(
            self.table_name,
            ', '.join(column_names),
            ', '.join(['?'] * len(column_names)),
        )

        # fill in repeated fields

        with self.conn:
            self.conn.execute(query, tuple(values_list))
            for name, subt in self.subfield_tables.items():
                subt.update_from()

        assert id_value is not None
        if self.update_cb is not None and call_cb:
            self.update_cb(id_value, updated_msg.SerializeToString())

    def delete(self, entity_id: str, call_cb: bool = True) -> None:
        pass
