# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from google.protobuf.descriptor import (
    Descriptor as google___protobuf___descriptor___Descriptor,
    FieldDescriptor as google___protobuf___descriptor___FieldDescriptor,
)

from google.protobuf.message import (
    Message as google___protobuf___message___Message,
)

from typing import (
    Optional as typing___Optional,
    Text as typing___Text,
    Union as typing___Union,
)

from typing_extensions import (
    Literal as typing_extensions___Literal,
)


builtin___bool = bool
builtin___bytes = bytes
builtin___float = float
builtin___int = int
if sys.version_info < (3,):
    builtin___buffer = buffer
    builtin___unicode = unicode


class DtsdbFieldOptions(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    is_id = ... # type: builtin___bool
    merge = ... # type: typing___Text

    def __init__(self,
        *,
        is_id : typing___Optional[builtin___bool] = None,
        merge : typing___Optional[typing___Text] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> DtsdbFieldOptions: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> DtsdbFieldOptions: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"is_id",b"is_id",u"merge",b"merge"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"is_id",b"is_id",u"merge",b"merge"]) -> None: ...
global___DtsdbFieldOptions = DtsdbFieldOptions

class DtsdbMessageOptions(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    name = ... # type: typing___Text

    def __init__(self,
        *,
        name : typing___Optional[typing___Text] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> DtsdbMessageOptions: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> DtsdbMessageOptions: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"name",b"name"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"name",b"name"]) -> None: ...
global___DtsdbMessageOptions = DtsdbMessageOptions

field = ... # type: google___protobuf___descriptor___FieldDescriptor

table = ... # type: google___protobuf___descriptor___FieldDescriptor