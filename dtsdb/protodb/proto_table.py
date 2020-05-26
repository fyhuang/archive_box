import sqlite3
from typing import Any, Optional, List, Callable

from google.protobuf.message import Message
from google.protobuf.descriptor import Descriptor, FieldDescriptor

from dtsdb import sqlite_util


def _protobuf_to_sqlite_type(field_type):
    if field_type in (FieldDescriptor.TYPE_BOOL):
        return "BOOLEAN"
    elif field_type in (FieldDescriptor.TYPE_BYTES):
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
            FieldDescriptor.TYPE_UINT64,
            FieldDescriptor.TYPE_ENUM):
        return "INTEGER"
    elif field_type in (FieldDescriptor.TYPE_STRING):
        return "TEXT"
    else:
        raise RuntimeError("Unsupported field type {}".format(field_type))


def _find_id_field(descriptor: Descriptor) -> FieldDescriptor:
    for field in descriptor.fields:
        if field.name == "id":
            return field
    raise RuntimeError("Message {} has no ID field".format(descriptor.name))


def entity_name(msg_class) -> str:
    return msg_class.DESCRIPTOR.name


class ProtoTable(object):
    """Stores messages in a table as encoded protobufs."""
    def __init__(self,
            conn: sqlite3.Connection,
            msg_class: Any,
            update_cb: Optional[Callable[[str, Optional[bytes]], Any]] = None,
            ) -> None:
        self.conn = conn
        self.msg_class = msg_class
        self.msg_descriptor = msg_class.DESCRIPTOR
        self.update_cb = update_cb

        self.id_field = _find_id_field(self.msg_descriptor)

        self.entity_name = entity_name(msg_class)
        self.table_name = "m_" + self.entity_name
        # TODO(fyhuang): support materializing individual fields for indexing
        self._init_table()

    def _init_table(self) -> None:
        if self.id_field.label == FieldDescriptor.LABEL_REQUIRED:
            id_column = "id TEXT NOT NULL"
        else:
            id_column = "id TEXT"

        create_table_schema = '''CREATE TABLE IF NOT EXISTS {tname} (
            {id_column},
            serialized_pb BLOB NOT NULL,
            
            PRIMARY KEY (id)
        )'''.format(
            tname=self.table_name,
            id_column=id_column,
        )

        sqlite_util.ensure_table_matches(self.conn, create_table_schema)

    def new(self) -> Any:
        return self.msg_class()

    def get(self, id: str) -> Optional[Any]:
        c = self.conn.cursor()
        row = c.execute("SELECT serialized_pb FROM {} WHERE id=?".format(self.table_name),
                (id,)).fetchone()
        if row is None:
            return None

        msg = self.new()
        msg.ParseFromString(row[0])
        return msg

    def getx(self, id: str) -> Any:
        result = self.get(id)
        if result is None:
            raise RuntimeError("Requested entity with ID {} but none found".format(id))
        return result

    def filter(self, filter_func: Callable[[Any], bool]) -> List[Any]:
        """Filter documents, in software, with the provided filter func."""
        return []

    def update(self, updated_msg: Message, call_cb: bool = True) -> None:
        serialized_msg = updated_msg.SerializeToString()
        query = "INSERT OR REPLACE INTO {} (id, serialized_pb) VALUES(?, ?)".format(self.table_name) 

        id_value = getattr(updated_msg, self.id_field.name)
        with self.conn:
            self.conn.execute(query, (id_value, serialized_msg))
        assert id_value is not None
        if self.update_cb is not None and call_cb:
            self.update_cb(id_value, serialized_msg)

    def delete(self, entity_id: str, call_cb: bool = True) -> None:
        pass
