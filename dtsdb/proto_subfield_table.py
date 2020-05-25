import sqlite3

from . import sqlite_util

# TODO(fyhuang): doesn't support message-typed values
class ProtoSubfieldTable(object):
    def __init__(self,
            conn: sqlite3.Connection,
            table_name_prefix: str,
            field_id: int,
            value_type: str,
            # key_type is only required for map fields
            key_type: str = "BLOB"
            ) -> None:
        self.conn = conn
        self.table_name = "{}__sub_{}".format(table_name_prefix, field_id)
        self.field_id = field_id
        self.value_type = value_type
        self.key_type = key_type

        create_table = '''CREATE TABLE {} (
            id TEXT,
            key {},
            value {}
        )'''.format(self.table_name, key_type, value_type)
        sqlite_util.ensure_table_matches(self.conn, create_table)
