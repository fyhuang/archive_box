import hashlib
from pathlib import Path

def local_fs_storage(data_id: str) -> Path:
    return Path(data_id[:4]) / data_id[4:]

def schema_01(file_obj) -> str:
    pass
