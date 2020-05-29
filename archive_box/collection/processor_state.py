import sqlite3
import threading
from datetime import datetime, timezone
from typing import Optional, List, NamedTuple

from dtsdb import sqlite_util


class WorkItem(NamedTuple):
    timestamp: datetime
    document_id: str
    action: str

    @staticmethod
    def from_row(row) -> 'WorkItem':
        return WorkItem(sqlite_util.parse_timestamp(row[0]), row[1], row[2])


class ProcessorState(object):
    def __init__(self, conn: sqlite3.Connection, cv: threading.Condition) -> None:
        # TODO(fyhuang): would be nice to be able to use ProtoTable for this
        self.conn = conn
        self.cv = cv

    def first_time_setup(self) -> None:
        schema = '''CREATE TABLE processor_work_queue (
            timestamp TIMESTAMP NOT NULL,
            document_id TEXT NOT NULL,
            action TEXT NOT NULL,

            PRIMARY KEY (timestamp)
        )'''
        sqlite_util.ensure_table_matches(self.conn, schema)

    def get_queue_size(self) -> int:
        c = self.conn.cursor()
        row = c.execute('SELECT COUNT(*) FROM processor_work_queue').fetchone()
        return row[0]

    def get_items_for_doc(self, doc_id) -> List[WorkItem]:
        c = self.conn.cursor()
        c.execute('SELECT * FROM processor_work_queue WHERE document_id=? ORDER BY timestamp',
                (doc_id,))
        return [WorkItem.from_row(row) for row in c]

    def peek_next_item(self) -> Optional[WorkItem]:
        c = self.conn.cursor()
        row = c.execute('SELECT * FROM processor_work_queue ORDER BY timestamp LIMIT 1').fetchone()
        if row is None:
            return None
        return WorkItem.from_row(row)

    def delete_item(self, item: WorkItem) -> None:
        with self.conn:
            self.conn.execute('DELETE FROM processor_work_queue WHERE timestamp=?',
                    (item.timestamp,))

    def add_work_item(self, document_id: str, action: str, timestamp: Optional[datetime] = None):
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        with self.conn:
            self.conn.execute('INSERT OR IGNORE INTO processor_work_queue VALUES (?,?,?)',
                    (timestamp, document_id, action))
        with self.cv:
            self.cv.notify()

    def wait_for_work(self, timeout=None) -> None:
        with self.cv:
            self.cv.wait(timeout)
