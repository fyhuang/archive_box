from pathlib import Path
from typing import List, Union

from archive_box.sdid import StoredDataId, file_to_sdid

from .scanner_state import *
from archive_box.workers import Worker
from archive_box.storage.local_file import LocalFileStorage


class ScannerWorker(Worker):
    def __init__(self,
            inbox_path: Union[str, Path],
            state: ScannerState,
            local_store: LocalFileStorage,
            ) -> None:
        Worker.__init__(self)
        self.inbox_path = Path(inbox_path)
        self.state = state
        self.local_store = local_store
        self.to_ingest: List[Path] = []

    def run(self):
        while not self.should_quit():
            self.scan_inbox()
            if self.should_quit():
                break
            self.ingest_all()
            self.wait_for_changes()

    def wait_for_changes(self) -> None:
        # TODO(fyhuang): actually implement filesystem watching
        self.quit_event.wait(timeout=5)

    def scan_inbox(self):
        for filename in self.inbox_path.glob("**/*"):
            self.to_ingest.append(Path(filename))

    def ingest_all(self):
        while len(self.to_ingest) > 0:
            if self.should_quit():
                break
            filename = self.to_ingest.pop()
            self.ingest_one_file(filename)

    def ingest_one_file(self, filename: Path) -> None:
        if self.state.is_already_scanned(filename):
            return

        print("Ingesting {}...".format(filename))
        sdid = file_to_sdid(filename)
        # TODO(fyhuang): delete/move in-place
        self.local_store.upload(sdid, filename)
        self.state.record_scanned_file(filename, sdid)
