import sys

from archive_box.workers import Worker
from archive_box.storage import LocalFileStorage
from .processor_state import *

class ProcessorWorker(Worker):
    def __init__(self,
            state: ProcessorState,
            local_store: LocalFileStorage,
            # TODO(fyhuang): generalize this storage
            remote_storage: LocalFileStorage,
            ) -> None:
        Worker.__init__(self)
        self.state = state
        self.local_store = local_store
        self.remote_storage = remote_storage

    def run(self) -> None:
        while not self.should_quit():
            self.state.wait_for_work(timeout=30.0)
            self.run_one()

    def run_one(self) -> None:
        next_item = self.state.peek_next_item()
        if next_item is None:
            return

        if next_item.action == "upload":
            raise NotImplementedError()
        else:
            print("Warning: unknown action {} while processing {}".format(next_item.action, next_item.document_id))

        self.state.delete_item(next_item)
