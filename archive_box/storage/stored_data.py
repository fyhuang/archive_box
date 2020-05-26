import hashlib
import datetime
from pathlib import Path
from typing import Tuple, NamedTuple

from archive_box.archive_box_pb2 import StoredDataId


def make_sdid(schema: str, id: str) -> StoredDataId:
    result = StoredDataId()
    result.schema = schema
    result.id = id
    return result


def sdid_to_tuple(sdid: StoredDataId) -> Tuple[str, str]:
    return (sdid.schema, sdid.id)


def sdid_to_str(sdid: StoredDataId):
    return "{}_{}".format(sdid.schema, sdid.id)


def sdid_schema_01(filename: Path) -> StoredDataId:
    h = hashlib.blake2b(digest_size=16, person=b'arbox')
    with filename.open("rb") as f:
        while True:
            chunk = f.read(1 * 1024 * 1024) # 1 MB chunk
            if len(chunk) == 0:
                # EOF reached
                break
            h.update(chunk)
    return make_sdid("01", h.digest().hex())


def file_to_sdid(filename: Path) -> StoredDataId:
    return sdid_schema_01(filename)


class StoredStat(NamedTuple):
    size_bytes: int
    upload_time: datetime.datetime
