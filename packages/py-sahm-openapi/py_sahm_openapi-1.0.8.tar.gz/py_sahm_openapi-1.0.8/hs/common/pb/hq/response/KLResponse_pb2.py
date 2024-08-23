# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: KLResponse.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database


# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

from hs.common.pb.hq.dto import Security_pb2 as hq_dot_dto_dot_Security__pb2 , KLine_pb2 as hq_dot_dto_dot_KLine__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='KLResponse.proto',
  package='',
  syntax='proto3',
  serialized_options=b'\n3com.huasheng.sa.quant.open.sdk.protobuf.hq.responseB\017KLResponseProto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x10KLResponse.proto\x1a\x15hq/dto/Security.proto\x1a\x12hq/dto/KLine.proto\"@\n\nKLResponse\x12\x1b\n\x08security\x18\x01 \x01(\x0b\x32\t.Security\x12\x15\n\x05kline\x18\x02 \x03(\x0b\x32\x06.KLineBF\n3com.huasheng.sa.quant.open.sdk.protobuf.hq.responseB\x0fKLResponseProtob\x06proto3'
  ,
  dependencies=[hq_dot_dto_dot_Security__pb2.DESCRIPTOR,hq_dot_dto_dot_KLine__pb2.DESCRIPTOR,])




_KLRESPONSE = _descriptor.Descriptor(
  name='KLResponse',
  full_name='KLResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='security', full_name='KLResponse.security', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='kline', full_name='KLResponse.kline', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=63,
  serialized_end=127,
)

_KLRESPONSE.fields_by_name['security'].message_type = hq_dot_dto_dot_Security__pb2._SECURITY
_KLRESPONSE.fields_by_name['kline'].message_type = hq_dot_dto_dot_KLine__pb2._KLINE
DESCRIPTOR.message_types_by_name['KLResponse'] = _KLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

KLResponse = _reflection.GeneratedProtocolMessageType('KLResponse', (_message.Message,), {
  'DESCRIPTOR' : _KLRESPONSE,
  '__module__' : 'KLResponse_pb2'
  # @@protoc_insertion_point(class_scope:KLResponse)
  })
_sym_db.RegisterMessage(KLResponse)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
