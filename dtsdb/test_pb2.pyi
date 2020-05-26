# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from google.protobuf.descriptor import (
    Descriptor as google___protobuf___descriptor___Descriptor,
    EnumDescriptor as google___protobuf___descriptor___EnumDescriptor,
)

from google.protobuf.internal.containers import (
    RepeatedScalarFieldContainer as google___protobuf___internal___containers___RepeatedScalarFieldContainer,
)

from google.protobuf.message import (
    Message as google___protobuf___message___Message,
)

from typing import (
    Iterable as typing___Iterable,
    List as typing___List,
    Optional as typing___Optional,
    Text as typing___Text,
    Tuple as typing___Tuple,
    Union as typing___Union,
    cast as typing___cast,
)

from typing_extensions import (
    Literal as typing_extensions___Literal,
)


builtin___bool = bool
builtin___bytes = bytes
builtin___float = float
builtin___int = int
builtin___str = str
if sys.version_info < (3,):
    builtin___buffer = buffer
    builtin___unicode = unicode


class Simple(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    id = ... # type: typing___Text
    opt_string = ... # type: typing___Text
    req_bool = ... # type: builtin___bool

    def __init__(self,
        *,
        id : typing___Optional[typing___Text] = None,
        opt_string : typing___Optional[typing___Text] = None,
        req_bool : typing___Optional[builtin___bool] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> Simple: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> Simple: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"id",b"id",u"opt_string",b"opt_string",u"req_bool",b"req_bool"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"id",b"id",u"opt_string",b"opt_string",u"req_bool",b"req_bool"]) -> None: ...
global___Simple = Simple

class Nested(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    class Selection(builtin___int):
        DESCRIPTOR: google___protobuf___descriptor___EnumDescriptor = ...
        @classmethod
        def Name(cls, number: builtin___int) -> builtin___str: ...
        @classmethod
        def Value(cls, name: builtin___str) -> 'Nested.Selection': ...
        @classmethod
        def keys(cls) -> typing___List[builtin___str]: ...
        @classmethod
        def values(cls) -> typing___List['Nested.Selection']: ...
        @classmethod
        def items(cls) -> typing___List[typing___Tuple[builtin___str, 'Nested.Selection']]: ...
        HELLO = typing___cast('Nested.Selection', 0)
        WORLD = typing___cast('Nested.Selection', 1)
    HELLO = typing___cast('Nested.Selection', 0)
    WORLD = typing___cast('Nested.Selection', 1)
    global___Selection = Selection

    class Inner(google___protobuf___message___Message):
        DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
        f1 = ... # type: typing___Text
        f2 = ... # type: builtin___int

        def __init__(self,
            *,
            f1 : typing___Optional[typing___Text] = None,
            f2 : typing___Optional[builtin___int] = None,
            ) -> None: ...
        if sys.version_info >= (3,):
            @classmethod
            def FromString(cls, s: builtin___bytes) -> Nested.Inner: ...
        else:
            @classmethod
            def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> Nested.Inner: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def HasField(self, field_name: typing_extensions___Literal[u"f1",b"f1",u"f2",b"f2"]) -> builtin___bool: ...
        def ClearField(self, field_name: typing_extensions___Literal[u"f1",b"f1",u"f2",b"f2"]) -> None: ...
    global___Inner = Inner

    id = ... # type: typing___Text
    selection = ... # type: global___Nested.Selection

    @property
    def inner(self) -> global___Nested.Inner: ...

    def __init__(self,
        *,
        id : typing___Optional[typing___Text] = None,
        selection : typing___Optional[global___Nested.Selection] = None,
        inner : typing___Optional[global___Nested.Inner] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> Nested: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> Nested: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"id",b"id",u"inner",b"inner",u"selection",b"selection"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"id",b"id",u"inner",b"inner",u"selection",b"selection"]) -> None: ...
global___Nested = Nested

class AdvancedTest(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    id = ... # type: typing___Text
    r_str = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text]

    def __init__(self,
        *,
        id : typing___Optional[typing___Text] = None,
        r_str : typing___Optional[typing___Iterable[typing___Text]] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> AdvancedTest: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> AdvancedTest: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"id",b"id"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"id",b"id",u"r_str",b"r_str"]) -> None: ...
global___AdvancedTest = AdvancedTest

class NoId(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    my_id = ... # type: typing___Text

    def __init__(self,
        *,
        my_id : typing___Optional[typing___Text] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> NoId: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> NoId: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"my_id",b"my_id"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"my_id",b"my_id"]) -> None: ...
global___NoId = NoId

class MergeTest(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    id = ... # type: typing___Text
    s_error = ... # type: typing___Text
    s_latest = ... # type: typing___Text
    r_i32_union = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[builtin___int]
    r_i32_lunion = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[builtin___int]

    def __init__(self,
        *,
        id : typing___Optional[typing___Text] = None,
        s_error : typing___Optional[typing___Text] = None,
        s_latest : typing___Optional[typing___Text] = None,
        r_i32_union : typing___Optional[typing___Iterable[builtin___int]] = None,
        r_i32_lunion : typing___Optional[typing___Iterable[builtin___int]] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> MergeTest: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> MergeTest: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"id",b"id",u"s_error",b"s_error",u"s_latest",b"s_latest"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"id",b"id",u"r_i32_lunion",b"r_i32_lunion",u"r_i32_union",b"r_i32_union",u"s_error",b"s_error",u"s_latest",b"s_latest"]) -> None: ...
global___MergeTest = MergeTest
