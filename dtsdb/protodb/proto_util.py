from typing import Any, Optional, List, NamedTuple, Generator

from google.protobuf.message import Message
from google.protobuf.descriptor import Descriptor, FieldDescriptor


class Pathfinder(object):
    def __init__(self, msg: Message, name_path: List[str]):
        self.msg = msg
        self.name_path = name_path

        self.container = msg
        for name in name_path[:-1]:
            self.container = getattr(self.container, name)

    def has(self) -> bool:
        return self.container.HasField(self.name_path[-1])

    def get(self) -> Any:
        return getattr(self.container, self.name_path[-1])

    def set(self, value: Any) -> None:
        setattr(self.container, self.name_path[-1], value)

    def clear(self) -> None:
        self.container.ClearField(self.name_path[-1])

    def copy(self, other: 'Pathfinder') -> None:
        # copy the value from the other Pathfinder, keeping set/unset
        if other.has():
            self.set(other.get())
        else:
            self.clear()


class NestedField(NamedTuple):
    name_path: List[str]
    desc: FieldDescriptor
    map_value: Optional[FieldDescriptor]


def iter_nested_fields(msg_descriptor: Descriptor) -> Generator[NestedField, None, None]:
    def recur(descriptor: Descriptor,
            name_path_prefix: List[str]):

        for field in descriptor.fields:
            name_path = name_path_prefix + [field.name]
            if field.message_type is not None:
                if field.message_type.GetOptions().map_entry:
                    # this field is actually a map<>, so don't recurse into it
                    # TODO(fyhuang): what about recursively merging the message values?
                    value_field = field.message_type.fields_by_name["value"]
                    yield NestedField(name_path, field, value_field)
                    continue
                else:
                    yield from recur(
                        field.message_type,
                        name_path,
                    )
                    continue

            yield NestedField(name_path, field, None)

    yield from recur(msg_descriptor, [])
