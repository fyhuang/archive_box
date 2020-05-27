import os
import sqlite3
import threading
import secrets
from typing import Dict
from pathlib import Path

import toml

from dtsdb.node_config import NodeConfig
from dtsdb.synced_db import SyncedDb

from . import archive_box_pb2 as pb2


class ColPool(object):
    def __init__(self, new_db) -> None:
        self.new_db = new_db
        self.lock = threading.Lock()

    def first_time_setup(self):
        self.new_db().first_time_setup()

    def get(self):
        return self.new_db()



class CollectionManager(object):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.internal = workspace / "internal"
        os.makedirs(self.internal, exist_ok=True)

        node_config_path = self.internal / "node_config.toml"
        if node_config_path.exists():
            with node_config_path.open("r") as f:
                self.node_config = NodeConfig.from_toml(f.read())
        else:
            self.node_config = NodeConfig(secrets.randbelow(2**63), os.getenv("HOSTNAME"))
            with node_config_path.open("w") as f:
                f.write(self.node_config.to_toml())

        with open(workspace / "config.toml", "r") as f:
            self.config = toml.load(f)

        self.pools: Dict[str, ColPool] = {}
        for cid in self.config.get("collections", {}).keys():
            pool = ColPool(self._new_db_func(cid))
            pool.first_time_setup()
            self.pools[cid] = pool

        self.lock = threading.Lock()

    def _new_db_func(self, cid: str):
        db_path = self.internal / (cid + ".db")
        conn = sqlite3.connect(str(db_path))
        return SyncedDb(conn, self.node_config, [pb2.Collection, pb2.Document])

    # TODO(fyhuang): add new collection at runtime

    # TODO(fyhuang): sync
    def maybe_sync(self) -> None:
        pass

    def col(self, cid: str):
        with self.lock:
            pool = self.pools[cid]
        return pool.get()
    

_mgr = None

def load_workspace(workspace: Path):
    global _mgr
    _mgr = CollectionManager(workspace)

def get() -> CollectionManager:
    if _mgr is None:
        raise RuntimeError("manager not yet initialized")
    return _mgr
