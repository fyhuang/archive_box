import sqlite3
import datetime
from pathlib import Path
from typing import List, Mapping, Union

from dtsdb.synced_db import SyncedDb
from dtsdb.node_config import NodeConfig

from archive_box import util
from archive_box import archive_box_pb2 as pb2
from archive_box.sdid import StoredDataId


_EXT_TO_MIMETYPE = {
        ".aac": "audio/aac",
        ".avi": "video/x-msvideo",
        ".epub": "application/epub+zip",
        ".gif": "image/gif",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".mov": "video/quicktime",
        ".mp3": "audio/mpeg",
        ".mp4": "video/mp4",
        ".mpeg": "video/mpeg",
        ".mkv": "video/webm", # TODO(fyhuang): not sure if this is 100% accurate
        ".oga": "audio/ogg",
        ".ogv": "video/ogg",
        ".opus": "audio/opus",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".ts": "video/mp2t",
        ".wav": "audio/wav",
        ".weba": "audio/webm",
        ".webm": "video/webm",
        ".webp": "image/webp",
        ".wmv": "video/x-ms-wmv",
}


def _now_ms() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000.0)


def _guess_mimetype(filepath: Union[str, Path]) -> str:
    # TODO(fyhuang): for containers (mp4/mkv), be smarter about whether they contain video or audio
    ext = Path(filepath).suffix.lower()
    return _EXT_TO_MIMETYPE[ext]


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
        document.data.main.sdid = sdid.to_strid()
        document.data.main.mime = _guess_mimetype(orig_filename)
    
        document.needs_review = True
        document.creation_time_ms = _now_ms()
        document.last_mod_time_ms = _now_ms()
    
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
