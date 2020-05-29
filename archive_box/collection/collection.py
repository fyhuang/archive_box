import sqlite3
import datetime
from typing import List, Mapping

from dtsdb.synced_db import SyncedDb
from dtsdb.node_config import NodeConfig

from archive_box import util
from archive_box import archive_box_pb2 as pb2
from archive_box.sdid import StoredDataId


def now_ms() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000.0)


class Collection(object):
    def __init__(
            self,
            conn: sqlite3.Connection,
            node_config: NodeConfig,
            config: Mapping,
            ) -> None:
        self.db = SyncedDb(conn, node_config, [pb2.Document])
        self.config = config

    def add_document(self, sdid: StoredDataId, orig_filename: str) -> None:
        document = pb2.Document()
        document.id = util.new_id()
        document.data_id = sdid.to_strid()
    
        document.needs_review = True
        document.creation_time_ms = now_ms()
        document.last_mod_time_ms = now_ms()
    
        document.display_name = orig_filename
        document.orig_filename = orig_filename
    
        self.db.get_table("Document").update(document)

    def docs_recent(self) -> List[pb2.Document]:
        return self.db.get_table("Document").queryall(
                sortkey=lambda d: d.creation_time_ms,
                reverse=True,
                limit=10
        )

    def docs_needs_review(self) -> List[pb2.Document]:
        return self.db.get_table("Document").queryall(
                filter=lambda d: d.needs_review,
                sortkey=lambda d: d.creation_time_ms,
                limit=10
        )
