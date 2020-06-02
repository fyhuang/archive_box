import hashlib
from pathlib import Path
from typing import Tuple, NamedTuple


class StoredDataId(NamedTuple):
    schema: str
    id: str

    @staticmethod
    def from_strid(sid: str) -> 'StoredDataId':
        schema_part, _, id_part = sid.partition("_")
        if schema_part is None or id_part is None:
            raise RuntimeError("Couldn't parse {}".format(sid))
        if len(schema_part) == 0 or len(id_part) == 0:
            raise RuntimeError("Couldn't parse {}".format(sid))

        return StoredDataId(schema_part, id_part)

    def to_strid(self) -> str:
        return "{}_{}".format(self.schema, self.id)

    def __str__(self) -> str:
        return self.to_strid()

    def __repr__(self) -> str:
        return self.to_strid()


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


if __name__ == "__main__":
    import sys
    print(file_to_sdid(Path(sys.argv[1])))
