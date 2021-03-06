import threading
from typing import Optional, Dict

from . import Worker


_workers: Dict[str, Worker] = {}
_threads: Dict[str, threading.Thread] = {}

def start_worker(w: Worker, name: Optional[str] = None) -> None:
    global _workers, _threads
    if name is None:
        name = type(w).__name__
    if name in _workers:
        raise RuntimeError("Worker {} already started".format(name))

    def target_func():
        w.run()
    _workers[name] = w
    _threads[name] = threading.Thread(target=target_func)
    _threads[name].start()


def stop_all_workers() -> None:
    for worker in _workers.values():
        worker.stop()

    for thread in _threads.values():
        thread.join()
