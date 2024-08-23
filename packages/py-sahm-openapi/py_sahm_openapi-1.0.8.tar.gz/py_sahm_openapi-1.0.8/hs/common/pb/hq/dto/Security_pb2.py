# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Security.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Security.proto',
  package='',
  syntax='proto3',
  serialized_options=b'\n.com.huasheng.sa.quant.open.sdk.protobuf.hq.dtoB\rSecurityProto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0eSecurity.proto\"/\n\x08Security\x12\x10\n\x08\x64\x61taType\x18\x01 \x01(\x05\x12\x11\n\tstockCode\x18\x02 \x01(\tB?\n.com.huasheng.sa.quant.open.sdk.protobuf.hq.dtoB\rSecurityProtob\x06proto3'
)




_SECURITY = _descriptor.Descriptor(
  name='Security',
  full_name='Security',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='dataType', full_name='Security.dataType', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='stockCode', full_name='Security.stockCode', index=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=65,
)

DESCRIPTOR.message_types_by_name['Security'] = _SECURITY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Security = _reflection.GeneratedProtocolMessageType('Security', (_message.Message,), {
  'DESCRIPTOR' : _SECURITY,
  '__module__' : 'Security_pb2'
  # @@protoc_insertion_point(class_scope:Security)
  })
_sym_db.RegisterMessage(Security)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
