import sqlite3
from pathlib import Path
from typing import List, NamedTuple, Union

from dtsdb import sqlite_util

from archive_box.sdid import StoredDataId
from archive_box.archive_box_pb2 import FilePointer


class ScannedFile(NamedTuple):
    path: Path
    pointer: FilePointer

    @staticmethod
    def from_row(row) -> 'ScannedFile':
        fp = FilePointer()
        fp.ParseFromString(row[2])
        return ScannedFile(Path(row[0]), fp)


class ScannerState(object):
    def __init__(self, conn: sqlite3.Connection, inbox_path: Union[str, Path]) -> None:
        # TODO(fyhuang): would be nice to be able to use ProtoTable for this
        self.conn = conn
        self.inbox_path = Path(inbox_path)

    def first_time_setup(self) -> None:
        # TODO(fyhuang): more attributes like mtime, size, etc. to make cache more robust
        schema = '''CREATE TABLE scanned_files (
            filepath STRING NOT NULL,
            sdid STRING NOT NULL,
            pointer BLOB NOT NULL,
            PRIMARY KEY (filepath)
        )'''
        sqlite_util.ensure_table_matches(self.conn, schema)

    # TODO(fyhuang): "is already ingested" probably a better name
    def is_already_scanned(self, path: Path) -> bool:
        c = self.conn.cursor()
        relative_path = path.relative_to(self.inbox_path)
        count = c.execute('SELECT COUNT(*) FROM scanned_files WHERE filepath=?',
                    (str(relative_path),)).fetchone()[0]
        return count > 0

    def get_all_scanned(self) -> List[ScannedFile]:
        result = []
        c = self.conn.cursor()
        for row in c.execute('SELECT * FROM scanned_files'):
            result.append(ScannedFile.from_row(row))
        return result

    def record_scanned_file(self, path: Path, pointer: FilePointer) -> None:
        relative_path = path.relative_to(self.inbox_path)
        with self.conn:
            self.conn.execute('INSERT OR IGNORE INTO scanned_files VALUES (?,?,?)',
                    (str(relative_path), pointer.sdid, pointer.SerializeToString()))

    def delete_scanned_file(self, sdid: StoredDataId) -> None:
        with self.conn:
            self.conn.execute('DELETE FROM scanned_files WHERE sdid=?',
                    (sdid.to_strid(),))
