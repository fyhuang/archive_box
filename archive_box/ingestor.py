import threading
import time
from functools import partial
from pathlib import Path
from typing import Union, List, Dict, Callable

from . import manager
from .storage import stored_data
from .storage.stored_data import StoredDataId


class Ingestor(object):
    def __init__(self,
            inbox_path: Union[Path, str],
            manager: manager.CollectionManager
            ) -> None:
        self.inbox_path = Path(inbox_path)
        self.manager = manager

        # TODO(fyhuang): store this state in db
        self.lock = threading.Lock()
        self.waiting: Dict[StoredDataId, Path] = {}
        self.target_collection: Dict[StoredDataId, str] = {}

        self.cache: Dict[Path, StoredDataId] = {}
        self.tasks: List[Callable] = []
        self.quit_event = threading.Event()

    def loop(self):
        while not self.quit_event.is_set():
            self.scan_inbox()
            if self.quit_event.is_set():
                break
            self.wait_for_changes()

    def get_waiting(self) -> Dict[StoredDataId, Path]:
        result = {}
        with self.lock:
            result.update(self.waiting)
        return result

    def set_target(self, sdid: StoredDataId, cid: str) -> None:
        with self.lock:
            self.target_collection[sdid] = cid

    def wait_for_changes(self) -> None:
        # TODO(fyhuang): remove this hack
        self.quit_event.wait(timeout=5)

    def scan_inbox(self):
        for filename in self.inbox_path.glob("**/*"):
            self.tasks.append(partial(self.scan_one_file, filename))

        # check for any scanned files that have target collections
        print("{} files awaiting upload".format(len(self.waiting)))
        target_collection = {}
        with self.lock:
            target_collection.update(self.target_collection)

        ready_to_upload = set(target_collection.keys()) & set(self.waiting.keys())
        print("{} files ready to upload".format(len(target_collection)))
        for sdid in ready_to_upload:
            self.tasks.append(partial(self.upload_one_file, sdid, target_collection[sdid]))

        while len(self.tasks) > 0:
            if self.quit_event.is_set():
                break
            task = self.tasks.pop()
            task()

    def scan_one_file(self, filename: Path) -> None:
        if filename in self.cache:
            print("Already cached {}".format(filename))
            return
        else:
            print("Scanning {}...".format(filename))

        sdid = stored_data.file_to_sdid(filename)
        with self.lock:
            self.waiting[sdid] = filename
        # TODO(fyhuang): cache on file size too
        self.cache[filename] = sdid

    def upload_one_file(self, sdid: StoredDataId, cid: str) -> None:
        print("Uploading {} to collection {}...".format(sdid, cid))
        self.manager.col(cid).storage.upload(sdid, self.waiting[sdid])
        with self.lock:
            del self.waiting[sdid]


_ingestor = None
_thread = None

def start_ingestor_thread() -> None:
    global _ingestor, _thread
    if _ingestor is not None:
        raise RuntimeError("ingestor is already running!")

    config = manager.get().config
    _ingestor = Ingestor(config["server"]["inbox"], manager.get())
    _thread = threading.Thread(target=_ingestor.loop)
    _thread.start()

def get() -> Ingestor:
    global _ingestor
    if _ingestor is None:
        raise RuntimeError("ingestor is not running!")
    return _ingestor

def stop_ingestor_thread() -> None:
    global _ingestor, _thread
    if _ingestor is None or _thread is None:
        return

    _ingestor.quit_event.set()
    print("Waiting for ingestor to finish...")
    _thread.join()
    _ingestor = None
    _thread = None
