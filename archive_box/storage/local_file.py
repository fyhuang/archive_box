import os
import io
import shutil
import functools
import datetime
from pathlib import Path
from typing import Optional, Tuple, Union, Any
from typing_extensions import Protocol

from archive_box.sdid import *
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


class ByteRangeReader(object):
    def __init__(self, wrapped_stream, max_bytes):
        self.wrapped_stream = wrapped_stream
        self.max_bytes = max_bytes
        self.read_so_far = 0

    def __enter__(self) -> Reader:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.wrapped_stream.__exit__(exc_type, exc_value, traceback)

    def read(self, wanted_size = -1):
        remaining = self.max_bytes - self.read_so_far
        if remaining <= 0:
            return b''

        if wanted_size < 0:
            read_size = remaining
        else:
            read_size = min(remaining, wanted_size)

        result = self.wrapped_stream.read(read_size)
        self.read_so_far += len(result)
        return result


class LocalFileStorage(object):
    def __init__(self, root_dir: Union[str, Path]):
        self.root = Path(root_dir).resolve()
        self.tempdir = self.root / "temp"
        os.makedirs(self.tempdir, exist_ok=True)

    def _to_path(self, sdid: StoredDataId) -> Path:
        first_part = sdid.schema + sdid.id[:2]
        return self.root / first_part / sdid.to_strid()

    def _is_path_in_root(self, path: Path) -> bool:
        path_abs = path.resolve()
        ancestor = _common_ancestor(self.root, path_abs)
        return ancestor == self.root

    def contains(self, sdid: StoredDataId) -> bool:
        path = self._to_path(sdid)
        return path.exists()

    def upload(self, sdid: StoredDataId, src_file: Path) -> None:
        path = self._to_path(sdid)
        if path.exists():
            return
        os.makedirs(path.parent, exist_ok=True)

        # Copy to a temp file first and then atomically move
        temp_path = self.tempdir / (sdid.to_strid() + ".tmp")
        shutil.copy2(src_file, temp_path)
        os.rename(temp_path, path)

    def delete(self, sdid: StoredDataId) -> None:
        raise NotImplementedError()

    def url_to(self, sdid: StoredDataId) -> str:
        return "file:///{}".format(self._to_path(sdid))

    def download_stat(self, sdid: StoredDataId) -> StoredStat:
        path = self._to_path(sdid)
        stat_result = os.stat(path)
        return StoredStat(
            stat_result.st_size,
            # TODO(fyhuang): what timezone? seems like local time in WSL
            datetime.datetime.fromtimestamp(stat_result.st_ctime)
        )

    def download_bytes(self, sdid: StoredDataId, byte_range: Optional[Tuple[int, int]] = None) -> Reader:
        # Both ends of the byte range are inclusive (like HTTP)
        path = self._to_path(sdid)
        f = path.open("rb")
        if byte_range is not None:
            f.seek(byte_range[0])
            return ByteRangeReader(f, byte_range[1] - byte_range[0] + 1)
        else:
            return f

    def download_to(self, sdid: StoredDataId, dest_filename: Path) -> None:
        with self.download_bytes(sdid) as src_f:
            with dest_filename.open("wb") as dest_f:
                shutil.copyfileobj(src_f, dest_f)

    def get_temp_filename(self) -> Path:
        # Get a filename that is compatible with `move_inplace`
        raise NotImplementedError()

    def move_inplace(self, sdid: StoredDataId, src_file: Path) -> None:
        # Move a pre-uploaded file into the right place
        # This is an internal function that allows LocalFileStorage to act like
        # a "zero-copy" cache
        if not self._is_path_in_root(src_file):
            raise RuntimeError("File should already be in the root to use move_inplace")

        path = self._to_path(sdid)
        if path.exists():
            return
        os.rename(src_file, path)

