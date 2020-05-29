import threading
from typing import Dict

from . import Worker


_workers: Dict[str, Worker] = {}
_threads: Dict[str, threading.Thread] = {}

def start_worker(w: Worker) -> None:
    global _workers, _threads
    name = type(w).__name__
    if name in _workers:
        raise RuntimeError("Worker {} already started".format(name))

    def target_func():
        w.run()
    _workers[name] = w
    _threads[name] = threading.Thread(target=target_func)
    _threads[name].start()
