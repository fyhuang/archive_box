import sqlite3
import datetime
from pathlib import Path
from typing import List, Mapping, Union

from dtsdb.protodb import ProtoTable
from dtsdb.synced_db import SyncedDb
from dtsdb.node_config import NodeConfig

from archive_box import util
from archive_box import archive_box_pb2 as pb2
from archive_box.sdid import StoredDataId
from . import document_files


def _now_ms() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000.0)


class Collection(object):
    def __init__(
            self,
            conn: sqlite3.Connection,
            node_config: NodeConfig,
            config: Mapping,
            ) -> None:
        self.docs = ProtoTable(conn, pb2.Document)
        self.synced_db = SyncedDb(conn, node_config, [self.docs])
        self.config = config

    def first_time_setup(self) -> None:
        self.docs.first_time_setup()
        self.synced_db.first_time_setup()

    def add_document(self, sdid: StoredDataId, orig_filename: str) -> str:
        document = pb2.Document()
        document.id = util.new_id()
        document.data.main.sdid = sdid.to_strid()
        document.data.main.mime = document_files.guess_mimetype(orig_filename)
    
        document.needs_review = True
        document.creation_time_ms = _now_ms()
        document.last_mod_time_ms = _now_ms()
    
        document.display_name = orig_filename
        document.orig_filename = orig_filename
    
        self.docs.update(document)
        return document.id

    def docs_recent(self) -> List[pb2.Document]:
        return self.docs.queryall(
                sortkey=lambda d: d.creation_time_ms,
                reverse=True,
                limit=10
        )

    def docs_needs_review(self) -> List[pb2.Document]:
        return self.docs.queryall(
                filter=lambda d: d.needs_review,
                sortkey=lambda d: d.creation_time_ms,
                limit=10
        )
