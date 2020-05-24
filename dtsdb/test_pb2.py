# type: ignore
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: test.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import schema_pb2 as schema__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='test.proto',
  package='dtsdb',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\ntest.proto\x12\x05\x64tsdb\x1a\x0cschema.proto\"^\n\x06Simple\x12\x12\n\x02id\x18\x01 \x02(\tB\x06\x82\xb5\x18\x02\x08\x01\x12 \n\nopt_string\x18\x02 \x01(\tB\x0c\x82\xb5\x18\x08\x12\x06latest\x12\x10\n\x08req_bool\x18\x03 \x02(\x08:\x0c\x82\xb5\x18\x08\n\x06Simple\"\xbe\x01\n\x06Nested\x12\x12\n\x02id\x18\x01 \x02(\tB\x06\x82\xb5\x18\x02\x08\x01\x12*\n\tselection\x18\x02 \x01(\x0e\x32\x17.dtsdb.Nested.Selection\x12\"\n\x05inner\x18\x03 \x01(\x0b\x32\x13.dtsdb.Nested.Inner\x1a\x1f\n\x05Inner\x12\n\n\x02\x66\x31\x18\x01 \x01(\t\x12\n\n\x02\x66\x32\x18\x02 \x02(\x05\"!\n\tSelection\x12\t\n\x05HELLO\x10\x00\x12\t\n\x05WORLD\x10\x01:\x0c\x82\xb5\x18\x08\n\x06Nested\"!\n\x0bNoTableName\x12\x12\n\x02id\x18\x01 \x02(\tB\x06\x82\xb5\x18\x02\x08\x01\"\x12\n\x04NoId:\n\x82\xb5\x18\x06\n\x04NoId'
  ,
  dependencies=[schema__pb2.DESCRIPTOR,])



_NESTED_SELECTION = _descriptor.EnumDescriptor(
  name='Selection',
  full_name='dtsdb.Nested.Selection',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='HELLO', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='WORLD', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=275,
  serialized_end=308,
)
_sym_db.RegisterEnumDescriptor(_NESTED_SELECTION)


_SIMPLE = _descriptor.Descriptor(
  name='Simple',
  full_name='dtsdb.Simple',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='dtsdb.Simple.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\002\010\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='opt_string', full_name='dtsdb.Simple.opt_string', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\010\022\006latest', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='req_bool', full_name='dtsdb.Simple.req_bool', index=2,
      number=3, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\202\265\030\010\n\006Simple',
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=35,
  serialized_end=129,
)


_NESTED_INNER = _descriptor.Descriptor(
  name='Inner',
  full_name='dtsdb.Nested.Inner',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='f1', full_name='dtsdb.Nested.Inner.f1', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='f2', full_name='dtsdb.Nested.Inner.f2', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
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
  serialized_start=242,
  serialized_end=273,
)

_NESTED = _descriptor.Descriptor(
  name='Nested',
  full_name='dtsdb.Nested',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='dtsdb.Nested.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\002\010\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='selection', full_name='dtsdb.Nested.selection', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='inner', full_name='dtsdb.Nested.inner', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_NESTED_INNER, ],
  enum_types=[
    _NESTED_SELECTION,
  ],
  serialized_options=b'\202\265\030\010\n\006Nested',
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=132,
  serialized_end=322,
)


_NOTABLENAME = _descriptor.Descriptor(
  name='NoTableName',
  full_name='dtsdb.NoTableName',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='dtsdb.NoTableName.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\202\265\030\002\010\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=324,
  serialized_end=357,
)


_NOID = _descriptor.Descriptor(
  name='NoId',
  full_name='dtsdb.NoId',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\202\265\030\006\n\004NoId',
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=359,
  serialized_end=377,
)

_NESTED_INNER.containing_type = _NESTED
_NESTED.fields_by_name['selection'].enum_type = _NESTED_SELECTION
_NESTED.fields_by_name['inner'].message_type = _NESTED_INNER
_NESTED_SELECTION.containing_type = _NESTED
DESCRIPTOR.message_types_by_name['Simple'] = _SIMPLE
DESCRIPTOR.message_types_by_name['Nested'] = _NESTED
DESCRIPTOR.message_types_by_name['NoTableName'] = _NOTABLENAME
DESCRIPTOR.message_types_by_name['NoId'] = _NOID
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Simple = _reflection.GeneratedProtocolMessageType('Simple', (_message.Message,), {
  'DESCRIPTOR' : _SIMPLE,
  '__module__' : 'test_pb2'
  # @@protoc_insertion_point(class_scope:dtsdb.Simple)
  })
_sym_db.RegisterMessage(Simple)

Nested = _reflection.GeneratedProtocolMessageType('Nested', (_message.Message,), {

  'Inner' : _reflection.GeneratedProtocolMessageType('Inner', (_message.Message,), {
    'DESCRIPTOR' : _NESTED_INNER,
    '__module__' : 'test_pb2'
    # @@protoc_insertion_point(class_scope:dtsdb.Nested.Inner)
    })
  ,
  'DESCRIPTOR' : _NESTED,
  '__module__' : 'test_pb2'
  # @@protoc_insertion_point(class_scope:dtsdb.Nested)
  })
_sym_db.RegisterMessage(Nested)
_sym_db.RegisterMessage(Nested.Inner)

NoTableName = _reflection.GeneratedProtocolMessageType('NoTableName', (_message.Message,), {
  'DESCRIPTOR' : _NOTABLENAME,
  '__module__' : 'test_pb2'
  # @@protoc_insertion_point(class_scope:dtsdb.NoTableName)
  })
_sym_db.RegisterMessage(NoTableName)

NoId = _reflection.GeneratedProtocolMessageType('NoId', (_message.Message,), {
  'DESCRIPTOR' : _NOID,
  '__module__' : 'test_pb2'
  # @@protoc_insertion_point(class_scope:dtsdb.NoId)
  })
_sym_db.RegisterMessage(NoId)


_SIMPLE.fields_by_name['id']._options = None
_SIMPLE.fields_by_name['opt_string']._options = None
_SIMPLE._options = None
_NESTED.fields_by_name['id']._options = None
_NESTED._options = None
_NOTABLENAME.fields_by_name['id']._options = None
_NOID._options = None
# @@protoc_insertion_point(module_scope)
