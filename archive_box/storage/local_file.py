import os
import io
import shutil
import functools
import datetime
from pathlib import Path
from typing import Optional, Tuple, Union, Any, Generator
from typing_extensions import Protocol

from archive_box import util
from archive_box.sdid import parse_sdid
from archive_box.byte_range import ByteRangeReader
from .stored_data import StoredStat


def _common_ancestor(p1: Path, p2: Path) -> Path:
    min_len = min(len(p1.parts), len(p2.parts))
    result = []
    for i in range(min_len):
        if p1.parts[i] != p2.parts[i]:
            break
        result.append(Path(p1.parts[i]))
    return functools.reduce(lambda a, b: a / b, result)


class Reader(Protocol):
    def __enter__(self) -> 'Reader':
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    def read(self, size = -1) -> bytes:
        pass


class LocalFileStorage(object):
    def __init__(self, root_dir: Union[str, Path]):
        self.root = Path(root_dir).resolve()
        self.tempdir = self.root / "temp"
        os.makedirs(self.tempdir, exist_ok=True)

    def _is_path_in_root(self, path: Path) -> bool:
        path_abs = path.resolve()
        ancestor = _common_ancestor(self.root, path_abs)
        return ancestor == self.root

    def path_to(self, sdid: str) -> Path:
        schema, id = parse_sdid(sdid)
        first_part = schema + id[:2]
        return self.root / first_part / sdid

    def contains(self, sdid: str) -> bool:
        path = self.path_to(sdid)
        return path.exists()

    def list(self) -> Generator[str, None, None]:
        # list the SDIDs stored
        for root, dirs, files in os.walk(self.root):
            if "temp" in dirs:
                # don't traverse the tempdir
                dirs.remove("temp")

            for file in files:
                try:
                    # make sure it is an SDID
                    schema, id = parse_sdid(file)
                    yield file
                except ValueError:
                    continue

    def upload(self, sdid: str, src_file: Path) -> None:
        path = self.path_to(sdid)
        if path.exists():
            return
        os.makedirs(path.parent, exist_ok=True)

        # Copy to a temp file first and then atomically move
        temp_path = self.tempdir / "upload_{}.tmp".format(sdid)
        shutil.copy2(src_file, temp_path)
        os.rename(temp_path, path)

    def delete(self, sdid: str) -> None:
        path = self.path_to(sdid)
        os.remove(path)
        os.removedirs(path.parent)

    def download_stat(self, sdid: str) -> StoredStat:
        path = self.path_to(sdid)
        stat_result = os.stat(path)
        return StoredStat(
            stat_result.st_size,
            # TODO(fyhuang): what timezone? seems like local time in WSL
            datetime.datetime.fromtimestamp(stat_result.st_ctime)
        )

    def download_bytes(self, sdid: str, byte_range: Optional[Tuple[int, int]] = None) -> Reader:
        # Both ends of the byte range are inclusive (like HTTP)
        path = self.path_to(sdid)
        f = path.open("rb")
        if byte_range is not None:
            return ByteRangeReader(f, byte_range[0], byte_range[1])
        else:
            return f

    def download_to(self, sdid: str, dest_filename: Path) -> None:
        with self.download_bytes(sdid) as src_f:
            with dest_filename.open("wb") as dest_f:
                shutil.copyfileobj(src_f, dest_f)

    def get_temp_filename(self) -> Path:
        # Get a filename that is compatible with `move_inplace`
        random_name = "download_{}.tmp".format(util.new_id())
        return self.tempdir / random_name

    def move_inplace(self, sdid: str, src_file: Path) -> None:
        # Move a pre-uploaded file into the right place
        # This is an internal function that allows LocalFileStorage to act like
        # a "zero-copy" cache
        if not self._is_path_in_root(src_file):
            raise RuntimeError("File should already be in the root to use move_inplace")

        path = self.path_to(sdid)
        if path.exists():
            return
        os.makedirs(path.parent, exist_ok=True)

        os.rename(src_file, path)

