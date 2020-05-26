import sqlite3
from typing import List

from dtsdb import sqlite_util

class FieldSpec(NamedTuple):
    name: str

class ProtoMessageTable(object):
    def __init__(self,
            conn: sqlite3.Connection,
            root_entity_name: str,
            field_name_flat: str,
            namepath_prefix: List[str],
            subfields: List[MsgField],
            container_type: str,
            ) -> None:
        self.conn = conn
        if len(field_name_flat) > 0:
            self.table_name = "m_{}__{}".format(root_entity_name, field_name_flat)
        else:
            self.table_name = "m_{}".format(root_entity_name)

        self.field_name_flat = field_name_flat
        self.namepath_prefix = namepath_prefix
        self.subfields = subfields

        create_table = '''CREATE TABLE {} (
            id TEXT,
            path BLOB,
            key BLOB,
            value {} NOT NULL
        )'''.format(self.table_name, key_type, value_type)
        sqlite_util.ensure_table_matches(self.conn, create_table)

    def update_from(self, id: str, container) -> None:
        if isinstance(container, list):
            print("A list")
        else:
            print("A map")

    def get_into_list(self, id: str, container) -> None:
        pass

    def get_into_map(self, id: str, container) -> None:
        pass

    def get_into_msg(self, id: str, container) -> None:
        pass
