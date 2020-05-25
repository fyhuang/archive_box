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
  serialized_pb=b'\n\x1d\x61rchive_box/archive_box.proto\x12\x0b\x61rchive_box\x1a\x12\x64tsdb/schema.proto\",\n\x0cStoredDataId\x12\x0e\n\x06schema\x18\x01 \x01(\t\x12\x0c\n\x04\x62lob\x18\x02 \x01(\t\"V\n\nCollection\x12\x12\n\x02id\x18\x01 \x02(\tB\x06\x82\xb5\x18\x02\x08\x01\x12\"\n\x0c\x64isplay_name\x18\x02 \x01(\tB\x0c\x82\xb5\x18\x08\x12\x06latest:\x10\x82\xb5\x18\x0c\n\nCollection\"\x99\x02\n\x08\x44ocument\x12\x12\n\x02id\x18\x01 \x02(\tB\x06\x82\xb5\x18\x02\x08\x01\x12*\n\x07\x64\x61ta_id\x18\x02 \x01(\x0b\x32\x19.archive_box.StoredDataId\x12\"\n\x0c\x64isplay_name\x18\x03 \x01(\tB\x0c\x82\xb5\x18\x08\x12\x06latest\x12\x1d\n\x04tags\x18\x04 \x03(\tB\x0f\x82\xb5\x18\x0b\x12\tset_union\x12I\n\x08metadata\x18\x05 \x03(\x0b\x32#.archive_box.Document.MetadataEntryB\x12\x82\xb5\x18\x0e\x12\x0cunion_latest\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01:\x0e\x82\xb5\x18\n\n\x08\x44ocument'
  ,
  dependencies=[dtsdb_dot_schema__pb2.DESCRIPTOR,])




_STOREDDATAID = _descriptor.Descriptor(
  name='StoredDataId',
  full_name='archive_box.StoredDataId',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='schema', full_name='archive_box.StoredDataId.schema', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='blob', full_name='archive_box.StoredDataId.blob', index=1,
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
  serialized_end=110,
)


_COLLECTION = _descriptor.Descriptor(
  name='Collection',
  full_name='archive_box.Collection',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='archive_box.Collection.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\002\010\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='display_name', full_name='archive_box.Collection.display_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\010\022\006latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\202\265\030\014\n\nCollection',
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=112,
  serialized_end=198,
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
  serialized_start=419,
  serialized_end=466,
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
      serialized_options=b'\202\265\030\002\010\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data_id', full_name='archive_box.Document.data_id', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='display_name', full_name='archive_box.Document.display_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\010\022\006latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tags', full_name='archive_box.Document.tags', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\013\022\tset_union', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metadata', full_name='archive_box.Document.metadata', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\016\022\014union_latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_DOCUMENT_METADATAENTRY, ],
  enum_types=[
  ],
  serialized_options=b'\202\265\030\n\n\010Document',
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=201,
  serialized_end=482,
)

_DOCUMENT_METADATAENTRY.containing_type = _DOCUMENT
_DOCUMENT.fields_by_name['data_id'].message_type = _STOREDDATAID
_DOCUMENT.fields_by_name['metadata'].message_type = _DOCUMENT_METADATAENTRY
DESCRIPTOR.message_types_by_name['StoredDataId'] = _STOREDDATAID
DESCRIPTOR.message_types_by_name['Collection'] = _COLLECTION
DESCRIPTOR.message_types_by_name['Document'] = _DOCUMENT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

StoredDataId = _reflection.GeneratedProtocolMessageType('StoredDataId', (_message.Message,), {
  'DESCRIPTOR' : _STOREDDATAID,
  '__module__' : 'archive_box.archive_box_pb2'
  # @@protoc_insertion_point(class_scope:archive_box.StoredDataId)
  })
_sym_db.RegisterMessage(StoredDataId)

Collection = _reflection.GeneratedProtocolMessageType('Collection', (_message.Message,), {
  'DESCRIPTOR' : _COLLECTION,
  '__module__' : 'archive_box.archive_box_pb2'
  # @@protoc_insertion_point(class_scope:archive_box.Collection)
  })
_sym_db.RegisterMessage(Collection)

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


_COLLECTION.fields_by_name['id']._options = None
_COLLECTION.fields_by_name['display_name']._options = None
_COLLECTION._options = None
_DOCUMENT_METADATAENTRY._options = None
_DOCUMENT.fields_by_name['id']._options = None
_DOCUMENT.fields_by_name['display_name']._options = None
_DOCUMENT.fields_by_name['tags']._options = None
_DOCUMENT.fields_by_name['metadata']._options = None
_DOCUMENT._options = None
# @@protoc_insertion_point(module_scope)
