import os
import sqlite3
import threading
import secrets
import socket
from typing import Any, Dict, NamedTuple, Callable
from pathlib import Path

import toml

from dtsdb.node_config import NodeConfig
from dtsdb.synced_db import SyncedDb

from . import archive_box_pb2 as pb2
from .storage import local_file


def _default_node_name():
    hostname = socket.gethostname()
    if len(hostname) == 0:
        return "unknown node"
    else:
        return hostname


class Collection(NamedTuple):
    config: Dict
    db: SyncedDb
    storage: Any


class ColPool(object):
    def __init__(self, new_col: Callable[[], Collection]) -> None:
        self.new_col = new_col
        self.lock = threading.Lock()

    def first_time_setup(self):
        self.new_col().db.first_time_setup()

    def get(self) -> Collection:
        return self.new_col()


class CollectionManager(object):
    def __init__(self, workspace: Path):
        if not workspace.exists():
            raise RuntimeError("workspace {} must exist already".format(workspace))

        self.workspace = workspace
        self.internal = workspace / "internal"
        os.makedirs(self.internal, exist_ok=True)

        node_config_path = self.internal / "node_config.toml"
        if node_config_path.exists():
            with node_config_path.open("r") as f:
                self.node_config = NodeConfig.from_toml(f.read())
        else:
            self.node_config = NodeConfig(secrets.randbelow(2**63), _default_node_name())
            with node_config_path.open("w") as f:
                f.write(self.node_config.to_toml())

        print("Starting node: {}".format(self.node_config))

        with open(workspace / "config.toml", "r") as f:
            self.config = toml.load(f)

        self.pools: Dict[str, ColPool] = {}
        for cid in self.config.get("collections", {}).keys():
            print("Found collection {}".format(cid))
            pool = ColPool(self._new_col_func(cid))
            pool.first_time_setup()
            self.pools[cid] = pool

        self.lock = threading.Lock()

    def _new_col_func(self, cid: str):
        def func() -> Collection:
            config = self.config["collections"][cid]

            db_path = self.internal / (cid + ".db")
            conn = sqlite3.connect(str(db_path))
            db = SyncedDb(conn, self.node_config, [pb2.Document])

            if config["storage"] == "local":
                storage = local_file.LocalFileStorage(Path(config["local_storage"]["root"]))
            else:
                raise RuntimeError("unknown storage type {}".format(config["storage"]))

            return Collection(config, db, storage)

        return func

    # TODO(fyhuang): sync
    def maybe_sync(self) -> bool:
        return False

    def col(self, cid: str) -> Collection:
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
