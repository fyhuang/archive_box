import threading
from abc import ABC, abstractmethod

class Worker(object):
    def __init__(self) -> None:
        self.quit_event = threading.Event()

    @abstractmethod
    def run(self) -> None:
        pass

    def should_quit(self) -> bool:
        return self.quit_event.is_set()

    def stop(self) -> None:
        self.quit_event.set()
