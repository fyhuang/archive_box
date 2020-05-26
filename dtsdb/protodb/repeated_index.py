from typing import Tuple

class RepeatedIndex(object):
    def __init__(self, parent_table, value_type):
        create_table = '''CREATE TABLE {} (
            id TEXT,
            index INTEGER,
            value {} NOT NULL,
            
            PRIMARY KEY(id, index)
        )'''.format(self.table_name, key_type, value_type)

        index = 'CREATE INDEX {} ON {} (value)'
            .format(index_name, table_name)

        sqlite_util.ensure_table_matches(self.conn, create_table)

    def ids_containing_subquery(self, value) -> Tuple[str, Tuple]:
        return (
            'SELECT DISTINCT id FROM {} WHERE value=?'.format(self.table_name),
            (value,)
        )



        # test stuff
        query = "SELECT {}.* FROM {} JOIN ({}) st1
