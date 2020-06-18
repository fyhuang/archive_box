import sqlite3
import typing
from typing import Any, Optional, List, Callable, Generic, TypeVar, Type

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


def _entity_name(msg_class) -> str:
    return msg_class.DESCRIPTOR.name


MsgT = TypeVar('MsgT', bound=Message)

class ProtoTable(Generic[MsgT]):
    """Stores messages in a table as encoded protobufs."""
    def __init__(self,
            conn: sqlite3.Connection,
            msg_class: Type[MsgT],
            ) -> None:
        self.conn = conn
        self.msg_class = msg_class
        self.msg_descriptor = msg_class.DESCRIPTOR
        self.callbacks: List[Callable[[str, Optional[bytes]], Any]] = []

        self.id_field = _find_id_field(self.msg_descriptor)

        self.entity_name = _entity_name(msg_class)
        self.table_name = "m_" + self.entity_name
        # TODO(fyhuang): support materializing individual fields for indexing

    def first_time_setup(self) -> None:
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

    def add_callback(self, callback: Callable[[str, Optional[bytes]], Any]) -> None:
        self.callbacks.append(callback)

    def new(self) -> MsgT:
        return self.msg_class()

    def get(self, id: str) -> Optional[MsgT]:
        c = self.conn.cursor()
        row = c.execute("SELECT serialized_pb FROM {} WHERE id=?".format(self.table_name),
                (id,)).fetchone()
        if row is None:
            return None

        msg = self.new()
        msg.ParseFromString(row[0])
        return msg

    def getx(self, id: str) -> MsgT:
        result = self.get(id)
        if result is None:
            raise RuntimeError("Requested entity with ID {} but none found".format(id))
        return result

    def getall(self, ids: List[str]) -> List[MsgT]:
        # TODO(fyhuang): can this be done in one query?
        return typing.cast(List[MsgT], list(
            filter(lambda x: x is not None, (self.get(id) for id in ids))
        ))

    def queryall(self,
            filter: Optional[Callable[[MsgT], bool]] = None,
            sortkey: Optional[Callable[[MsgT], Any]] = None,
            reverse: bool = False,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            ) -> List[MsgT]:
        """Filter and order documents, in software, with the provided filter func."""
        results = []
        c = self.conn.cursor()
        for row in c.execute("SELECT serialized_pb FROM {}".format(self.table_name)):
            msg = self.new()
            msg.ParseFromString(row[0])
            if filter is not None and (not filter(msg)):
                continue
            results.append(msg)

        # sort
        after_sort = results
        if sortkey:
            after_sort.sort(key=sortkey, reverse=reverse)

        # limit
        if offset is not None:
            after_sort = after_sort[offset:]
        if limit is not None:
            after_sort = after_sort[:limit]
        return after_sort

    def update(self, updated_msg: Message, call_cb: bool = True) -> None:
        serialized_msg = updated_msg.SerializeToString()
        query = "INSERT OR REPLACE INTO {} (id, serialized_pb) VALUES(?, ?)".format(self.table_name) 

        id_value = getattr(updated_msg, self.id_field.name)
        with self.conn:
            self.conn.execute(query, (id_value, serialized_msg))
        assert id_value is not None
        if call_cb:
            for cb in self.callbacks:
                cb(id_value, serialized_msg)

    def delete(self, entity_id: str, call_cb: bool = True) -> None:
        pass
