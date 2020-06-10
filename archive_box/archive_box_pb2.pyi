# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from google.protobuf.descriptor import (
    Descriptor as google___protobuf___descriptor___Descriptor,
)

from google.protobuf.internal.containers import (
    RepeatedScalarFieldContainer as google___protobuf___internal___containers___RepeatedScalarFieldContainer,
)

from google.protobuf.message import (
    Message as google___protobuf___message___Message,
)

from typing import (
    Iterable as typing___Iterable,
    Mapping as typing___Mapping,
    MutableMapping as typing___MutableMapping,
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


class FilePointer(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    sdid = ... # type: typing___Text
    mime = ... # type: typing___Text

    def __init__(self,
        *,
        sdid : typing___Optional[typing___Text] = None,
        mime : typing___Optional[typing___Text] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> FilePointer: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> FilePointer: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"mime",b"mime",u"sdid",b"sdid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"mime",b"mime",u"sdid",b"sdid"]) -> None: ...
global___FilePointer = FilePointer

class FileGroup(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    class MediaFormatsEntry(google___protobuf___message___Message):
        DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
        key = ... # type: typing___Text

        @property
        def value(self) -> global___FilePointer: ...

        def __init__(self,
            *,
            key : typing___Optional[typing___Text] = None,
            value : typing___Optional[global___FilePointer] = None,
            ) -> None: ...
        if sys.version_info >= (3,):
            @classmethod
            def FromString(cls, s: builtin___bytes) -> FileGroup.MediaFormatsEntry: ...
        else:
            @classmethod
            def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> FileGroup.MediaFormatsEntry: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def HasField(self, field_name: typing_extensions___Literal[u"key",b"key",u"value",b"value"]) -> builtin___bool: ...
        def ClearField(self, field_name: typing_extensions___Literal[u"key",b"key",u"value",b"value"]) -> None: ...
    global___MediaFormatsEntry = MediaFormatsEntry


    @property
    def main(self) -> global___FilePointer: ...

    @property
    def thumbnail(self) -> global___FilePointer: ...

    @property
    def preview(self) -> global___FilePointer: ...

    @property
    def media_formats(self) -> typing___MutableMapping[typing___Text, global___FilePointer]: ...

    def __init__(self,
        *,
        main : typing___Optional[global___FilePointer] = None,
        thumbnail : typing___Optional[global___FilePointer] = None,
        preview : typing___Optional[global___FilePointer] = None,
        media_formats : typing___Optional[typing___Mapping[typing___Text, global___FilePointer]] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> FileGroup: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> FileGroup: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"main",b"main",u"preview",b"preview",u"thumbnail",b"thumbnail"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"main",b"main",u"media_formats",b"media_formats",u"preview",b"preview",u"thumbnail",b"thumbnail"]) -> None: ...
global___FileGroup = FileGroup

class Document(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    class MetadataEntry(google___protobuf___message___Message):
        DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
        key = ... # type: typing___Text
        value = ... # type: typing___Text

        def __init__(self,
            *,
            key : typing___Optional[typing___Text] = None,
            value : typing___Optional[typing___Text] = None,
            ) -> None: ...
        if sys.version_info >= (3,):
            @classmethod
            def FromString(cls, s: builtin___bytes) -> Document.MetadataEntry: ...
        else:
            @classmethod
            def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> Document.MetadataEntry: ...
        def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
        def HasField(self, field_name: typing_extensions___Literal[u"key",b"key",u"value",b"value"]) -> builtin___bool: ...
        def ClearField(self, field_name: typing_extensions___Literal[u"key",b"key",u"value",b"value"]) -> None: ...
    global___MetadataEntry = MetadataEntry

    id = ... # type: typing___Text
    creation_time_ms = ... # type: builtin___int
    last_mod_time_ms = ... # type: builtin___int
    needs_review = ... # type: builtin___bool
    display_name = ... # type: typing___Text
    tags = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text]
    description = ... # type: typing___Text
    orig_filename = ... # type: typing___Text
    downloaded_from_url = ... # type: typing___Text
    auto_summary = ... # type: typing___Text
    auto_keywords = ... # type: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text]

    @property
    def data(self) -> global___FileGroup: ...

    @property
    def metadata(self) -> typing___MutableMapping[typing___Text, typing___Text]: ...

    def __init__(self,
        *,
        id : typing___Optional[typing___Text] = None,
        data : typing___Optional[global___FileGroup] = None,
        creation_time_ms : typing___Optional[builtin___int] = None,
        last_mod_time_ms : typing___Optional[builtin___int] = None,
        needs_review : typing___Optional[builtin___bool] = None,
        display_name : typing___Optional[typing___Text] = None,
        tags : typing___Optional[typing___Iterable[typing___Text]] = None,
        description : typing___Optional[typing___Text] = None,
        metadata : typing___Optional[typing___Mapping[typing___Text, typing___Text]] = None,
        orig_filename : typing___Optional[typing___Text] = None,
        downloaded_from_url : typing___Optional[typing___Text] = None,
        auto_summary : typing___Optional[typing___Text] = None,
        auto_keywords : typing___Optional[typing___Iterable[typing___Text]] = None,
        ) -> None: ...
    if sys.version_info >= (3,):
        @classmethod
        def FromString(cls, s: builtin___bytes) -> Document: ...
    else:
        @classmethod
        def FromString(cls, s: typing___Union[builtin___bytes, builtin___buffer, builtin___unicode]) -> Document: ...
    def MergeFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def CopyFrom(self, other_msg: google___protobuf___message___Message) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"auto_summary",b"auto_summary",u"creation_time_ms",b"creation_time_ms",u"data",b"data",u"description",b"description",u"display_name",b"display_name",u"downloaded_from_url",b"downloaded_from_url",u"id",b"id",u"last_mod_time_ms",b"last_mod_time_ms",u"needs_review",b"needs_review",u"orig_filename",b"orig_filename"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"auto_keywords",b"auto_keywords",u"auto_summary",b"auto_summary",u"creation_time_ms",b"creation_time_ms",u"data",b"data",u"description",b"description",u"display_name",b"display_name",u"downloaded_from_url",b"downloaded_from_url",u"id",b"id",u"last_mod_time_ms",b"last_mod_time_ms",u"metadata",b"metadata",u"needs_review",b"needs_review",u"orig_filename",b"orig_filename",u"tags",b"tags"]) -> None: ...
global___Document = Document
