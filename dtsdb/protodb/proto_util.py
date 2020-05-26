from typing import Any, List

from google.protobuf.message import Message

# TODO(fyhuang): also support fieldnum paths in addition to name paths
class Pathfinder(object):
    def __init__(self, msg: Message, name_path: List[str]):
        self.msg = msg
        self.name_path = name_path

        self.container = msg
        for name in name_path[:-1]:
            self.container = getattr(self.container, name)

    def get(self) -> Any:
        return getattr(self.container, self.name_path[-1])

    def set(self, value: Any) -> None:
        setattr(self.container, self.name_path[-1], value)
