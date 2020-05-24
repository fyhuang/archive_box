import os
import shutil
from pathlib import Path

from .stored_data import StoredDataId

class LocalFileStorage(object):
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.tempdir = root_dir / "temp"
        os.makedirs(self.tempdir, exist_ok=True)

    def _to_path(self, sdid: StoredDataId) -> Path:
        first_part = sdid.schema + sdid.id[:2]
        return self.root / first_part / sdid.id

    def contains(self, sdid: StoredDataId) -> bool:
        path = self._to_path(sdid)
        return path.exists()

    def store(self, src_file, sdid) -> None:
        path = self._to_path(sdid)
        if path.exists():
            return

        # In case src_file and root are on different filesystems,
        # copy to a temp file first and then atomically move
        temp_path = self.tempdir / sdid.to_strid() + ".tmp"
        shutil.copy2(src_file, temp_path)
        os.rename(temp_path, path)


