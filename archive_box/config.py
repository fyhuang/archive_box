from typing import Dict, NamedTuple

import toml

class CollectionConfig(NamedTuple):
    id: str
    storage_type: str
    storage_path: str
    remote_db_path: str

class Config(NamedTuple):
    collections: Dict[str, CollectionConfig]
