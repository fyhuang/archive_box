import inspect
import zipfile
from pathlib import Path

def load_extern_zipfile_interior(zipfile_relative_path: Path, interior_path: str) -> bytes:
    import archive_box
    package_path = Path(inspect.getfile(archive_box)).resolve().parent
    root_path = package_path.parent
    zipfile_path = root_path / zipfile_relative_path
    with zipfile.ZipFile(zipfile_path, "r") as zip:
        with zip.open(interior_path, "rb") as f:
            return f.read()
