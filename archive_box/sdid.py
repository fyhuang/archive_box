import hashlib
from pathlib import Path
from typing import Tuple, NamedTuple


def parse_sdid(sid: str) -> Tuple[str, str]:
    schema_part, _, id_part = sid.partition("_")
    if len(schema_part) != 2 or len(id_part) == 0:
        raise ValueError("Couldn't parse {}".format(sid))
    return (schema_part, id_part)


def make_sdid(schema_part: str, id_part: str) -> str:
    return "{}_{}".format(schema_part, id_part)


def sdid_schema_01(filename: Path) -> str:
    h = hashlib.blake2b(digest_size=16, person=b'arbox')
    with filename.open("rb") as f:
        while True:
            chunk = f.read(1 * 1024 * 1024) # 1 MB chunk
            if len(chunk) == 0:
                # EOF reached
                break
            h.update(chunk)
    return make_sdid("01", h.digest().hex())


def file_to_sdid(filename: Path) -> str:
    return sdid_schema_01(filename)


if __name__ == "__main__":
    import sys
    print(file_to_sdid(Path(sys.argv[1])))
