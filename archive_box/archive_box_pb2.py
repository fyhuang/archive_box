# type: ignore
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: archive_box/archive_box.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from dtsdb import schema_pb2 as dtsdb_dot_schema__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='archive_box/archive_box.proto',
  package='archive_box',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1d\x61rchive_box/archive_box.proto\x12\x0b\x61rchive_box\x1a\x12\x64tsdb/schema.proto\")\n\x0b\x46ilePointer\x12\x0c\n\x04sdid\x18\x01 \x02(\t\x12\x0c\n\x04mime\x18\x02 \x01(\t\"\x9b\x02\n\tFileGroup\x12&\n\x04main\x18\x01 \x02(\x0b\x32\x18.archive_box.FilePointer\x12+\n\tthumbnail\x18\x02 \x01(\x0b\x32\x18.archive_box.FilePointer\x12)\n\x07preview\x18\x03 \x01(\x0b\x32\x18.archive_box.FilePointer\x12?\n\rmedia_formats\x18\x04 \x03(\x0b\x32(.archive_box.FileGroup.MediaFormatsEntry\x1aM\n\x11MediaFormatsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\'\n\x05value\x18\x02 \x01(\x0b\x32\x18.archive_box.FilePointer:\x02\x38\x01\"\xf1\x03\n\x08\x44ocument\x12\n\n\x02id\x18\x01 \x02(\t\x12$\n\x04\x64\x61ta\x18\x02 \x02(\x0b\x32\x16.archive_box.FileGroup\x12\x18\n\x10\x63reation_time_ms\x18\n \x02(\x04\x12&\n\x10last_mod_time_ms\x18\x0b \x02(\x04\x42\x0c\x82\xb5\x18\x08\x12\x06latest\x12\"\n\x0cneeds_review\x18\x14 \x02(\x08\x42\x0c\x82\xb5\x18\x08\x12\x06latest\x12\x1b\n\x05title\x18\x15 \x01(\tB\x0c\x82\xb5\x18\x08\x12\x06latest\x12\x1d\n\x04tags\x18\x16 \x03(\tB\x0f\x82\xb5\x18\x0b\x12\tset_union\x12!\n\x0b\x64\x65scription\x18\x17 \x01(\tB\x0c\x82\xb5\x18\x08\x12\x06latest\x12I\n\x08metadata\x18\x1e \x03(\x0b\x32#.archive_box.Document.MetadataEntryB\x12\x82\xb5\x18\x0e\x12\x0cunion_latest\x12\x15\n\rorig_filename\x18\x64 \x01(\t\x12\x1b\n\x13\x64ownloaded_from_url\x18\x65 \x01(\t\x12\x15\n\x0c\x61uto_summary\x18\xc8\x01 \x01(\t\x12\'\n\rauto_keywords\x18\xc9\x01 \x03(\tB\x0f\x82\xb5\x18\x0b\x12\tset_union\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01'
  ,
  dependencies=[dtsdb_dot_schema__pb2.DESCRIPTOR,])




_FILEPOINTER = _descriptor.Descriptor(
  name='FilePointer',
  full_name='archive_box.FilePointer',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sdid', full_name='archive_box.FilePointer.sdid', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='mime', full_name='archive_box.FilePointer.mime', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=66,
  serialized_end=107,
)


_FILEGROUP_MEDIAFORMATSENTRY = _descriptor.Descriptor(
  name='MediaFormatsEntry',
  full_name='archive_box.FileGroup.MediaFormatsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='archive_box.FileGroup.MediaFormatsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='archive_box.FileGroup.MediaFormatsEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=316,
  serialized_end=393,
)

_FILEGROUP = _descriptor.Descriptor(
  name='FileGroup',
  full_name='archive_box.FileGroup',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='main', full_name='archive_box.FileGroup.main', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='thumbnail', full_name='archive_box.FileGroup.thumbnail', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='preview', full_name='archive_box.FileGroup.preview', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='media_formats', full_name='archive_box.FileGroup.media_formats', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_FILEGROUP_MEDIAFORMATSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=110,
  serialized_end=393,
)


_DOCUMENT_METADATAENTRY = _descriptor.Descriptor(
  name='MetadataEntry',
  full_name='archive_box.Document.MetadataEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='archive_box.Document.MetadataEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='archive_box.Document.MetadataEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=846,
  serialized_end=893,
)

_DOCUMENT = _descriptor.Descriptor(
  name='Document',
  full_name='archive_box.Document',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='archive_box.Document.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='archive_box.Document.data', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='creation_time_ms', full_name='archive_box.Document.creation_time_ms', index=2,
      number=10, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='last_mod_time_ms', full_name='archive_box.Document.last_mod_time_ms', index=3,
      number=11, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\010\022\006latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='needs_review', full_name='archive_box.Document.needs_review', index=4,
      number=20, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\010\022\006latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='title', full_name='archive_box.Document.title', index=5,
      number=21, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\010\022\006latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tags', full_name='archive_box.Document.tags', index=6,
      number=22, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\013\022\tset_union', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='description', full_name='archive_box.Document.description', index=7,
      number=23, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\010\022\006latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metadata', full_name='archive_box.Document.metadata', index=8,
      number=30, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\016\022\014union_latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='orig_filename', full_name='archive_box.Document.orig_filename', index=9,
      number=100, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='downloaded_from_url', full_name='archive_box.Document.downloaded_from_url', index=10,
      number=101, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='auto_summary', full_name='archive_box.Document.auto_summary', index=11,
      number=200, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='auto_keywords', full_name='archive_box.Document.auto_keywords', index=12,
      number=201, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\013\022\tset_union', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_DOCUMENT_METADATAENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=396,
  serialized_end=893,
)

_FILEGROUP_MEDIAFORMATSENTRY.fields_by_name['value'].message_type = _FILEPOINTER
_FILEGROUP_MEDIAFORMATSENTRY.containing_type = _FILEGROUP
_FILEGROUP.fields_by_name['main'].message_type = _FILEPOINTER
_FILEGROUP.fields_by_name['thumbnail'].message_type = _FILEPOINTER
_FILEGROUP.fields_by_name['preview'].message_type = _FILEPOINTER
_FILEGROUP.fields_by_name['media_formats'].message_type = _FILEGROUP_MEDIAFORMATSENTRY
_DOCUMENT_METADATAENTRY.containing_type = _DOCUMENT
_DOCUMENT.fields_by_name['data'].message_type = _FILEGROUP
_DOCUMENT.fields_by_name['metadata'].message_type = _DOCUMENT_METADATAENTRY
DESCRIPTOR.message_types_by_name['FilePointer'] = _FILEPOINTER
DESCRIPTOR.message_types_by_name['FileGroup'] = _FILEGROUP
DESCRIPTOR.message_types_by_name['Document'] = _DOCUMENT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FilePointer = _reflection.GeneratedProtocolMessageType('FilePointer', (_message.Message,), {
  'DESCRIPTOR' : _FILEPOINTER,
  '__module__' : 'archive_box.archive_box_pb2'
  # @@protoc_insertion_point(class_scope:archive_box.FilePointer)
  })
_sym_db.RegisterMessage(FilePointer)

FileGroup = _reflection.GeneratedProtocolMessageType('FileGroup', (_message.Message,), {

  'MediaFormatsEntry' : _reflection.GeneratedProtocolMessageType('MediaFormatsEntry', (_message.Message,), {
    'DESCRIPTOR' : _FILEGROUP_MEDIAFORMATSENTRY,
    '__module__' : 'archive_box.archive_box_pb2'
    # @@protoc_insertion_point(class_scope:archive_box.FileGroup.MediaFormatsEntry)
    })
  ,
  'DESCRIPTOR' : _FILEGROUP,
  '__module__' : 'archive_box.archive_box_pb2'
  # @@protoc_insertion_point(class_scope:archive_box.FileGroup)
  })
_sym_db.RegisterMessage(FileGroup)
_sym_db.RegisterMessage(FileGroup.MediaFormatsEntry)

Document = _reflection.GeneratedProtocolMessageType('Document', (_message.Message,), {

  'MetadataEntry' : _reflection.GeneratedProtocolMessageType('MetadataEntry', (_message.Message,), {
    'DESCRIPTOR' : _DOCUMENT_METADATAENTRY,
    '__module__' : 'archive_box.archive_box_pb2'
    # @@protoc_insertion_point(class_scope:archive_box.Document.MetadataEntry)
    })
  ,
  'DESCRIPTOR' : _DOCUMENT,
  '__module__' : 'archive_box.archive_box_pb2'
  # @@protoc_insertion_point(class_scope:archive_box.Document)
  })
_sym_db.RegisterMessage(Document)
_sym_db.RegisterMessage(Document.MetadataEntry)


_FILEGROUP_MEDIAFORMATSENTRY._options = None
_DOCUMENT_METADATAENTRY._options = None
_DOCUMENT.fields_by_name['last_mod_time_ms']._options = None
_DOCUMENT.fields_by_name['needs_review']._options = None
_DOCUMENT.fields_by_name['title']._options = None
_DOCUMENT.fields_by_name['tags']._options = None
_DOCUMENT.fields_by_name['description']._options = None
_DOCUMENT.fields_by_name['metadata']._options = None
_DOCUMENT.fields_by_name['auto_keywords']._options = None
# @@protoc_insertion_point(module_scope)
