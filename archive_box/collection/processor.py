
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

    def run(self):
        pass
