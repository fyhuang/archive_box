import hashlib
import datetime
from pathlib import Path
from typing import NamedTuple


class StoredDataId(NamedTuple):
    schema: str
    id: str

    def to_strid(self):
        return self.schema + self.id


def sdid_schema_01(filename: Path) -> StoredDataId:
    h = hashlib.blake2b(digest_size=16, person=b'arbox')
    with filename.open("rb") as f:
        while True:
            chunk = f.read(1 * 1024 * 1024) # 1 MB chunk
            if len(chunk) == 0:
                # EOF reached
                break
            h.update(chunk)
    return StoredDataId("01", h.digest().hex())


def file_to_sdid(filename: Path) -> StoredDataId:
    return sdid_schema_01(filename)


class StoredStat(NamedTuple):
    size_bytes: int
    upload_time: datetime.datetime