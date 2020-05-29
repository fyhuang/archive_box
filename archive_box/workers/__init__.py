import threading
from abc import ABC, abstractmethod

class Worker(object):
    def __init__(self):
        self.quit_event = threading.Event()

    @abstractmethod
    def run(self):
        pass

    def should_quit(self):
        return self.quit_event.is_set()

    def stop(self):
        self.quit_event.set()
