import sqlite3
import threading
from pathlib import Path
from typing import Optional, Callable

from . import api, scanner, collection, storage
from .workspace import Workspace


class Factory(object):
    def __init__(self,
            workspace: Workspace,
            scanner_cpool: Callable[[], sqlite3.Connection],
            collection_cpool: Callable[[str], sqlite3.Connection],
            ) -> None:
        self.workspace = workspace
        self.scanner_cpool = scanner_cpool
        self.collection_cpool = collection_cpool
        self.local_store = storage.LocalFileStorage(self.workspace.internal_path / "local_store")
        self.processor_cv = threading.Condition()

    @staticmethod
    def with_naive_cpools(workspace: Workspace) -> 'Factory':
        return Factory(
                workspace,
                lambda: sqlite3.connect(str(workspace.scanner_db_path())),
                lambda c: sqlite3.connect(str(workspace.collection_db_path(c))),
        )

    def first_time_setup(self) -> None:
        self.new_scanner_state().first_time_setup()
        for cid in self.workspace.cids():
            self.new_processor_state(cid).first_time_setup()
            self.new_collection(cid).first_time_setup()

    def new_scanner_state(self) -> scanner.ScannerState:
        conn = self.scanner_cpool()
        return scanner.ScannerState(conn, self.workspace.inbox_path())

    def new_scanner_worker(self) -> scanner.ScannerWorker:
        return scanner.ScannerWorker(
                self.workspace.inbox_path(),
                self.new_scanner_state(),
                self.local_store
        )

    def new_collection_storage(self, cid: str) -> storage.LocalFileStorage:
        config = self.workspace.collection_config(cid)
        if config.storage == "local":
            return storage.LocalFileStorage(config.local_storage["root"])
        else:
            raise RuntimeError("Unknown storage type {}".format(config.storage))

    def new_processor_state(self, cid: str) -> collection.ProcessorState:
        conn = self.collection_cpool(cid)
        # TODO(fyhuang): technically, separate CV per collection would be more efficient
        return collection.ProcessorState(conn, self.processor_cv)

    def new_processor_worker(self, cid: str) -> collection.ProcessorWorker:
        storage = self.new_collection_storage(cid)
        coll = self.new_collection(cid)
        return collection.ProcessorWorker(
                self.new_processor_state(cid),
                coll,
                self.local_store,
                storage,
                coll.search_index,
        )

    def new_collection(self, cid: str) -> collection.Collection:
        conn = self.collection_cpool(cid)
        return collection.Collection(
                conn,
                self.workspace.node_config,
                self.workspace.collection_config(cid),
        )

    def new_api(self, cid: str) -> api.ArchiveBoxApi:
        return api.ArchiveBoxApi(
                self.new_collection(cid),
                self.new_processor_state(cid),
                self.local_store,
        )
