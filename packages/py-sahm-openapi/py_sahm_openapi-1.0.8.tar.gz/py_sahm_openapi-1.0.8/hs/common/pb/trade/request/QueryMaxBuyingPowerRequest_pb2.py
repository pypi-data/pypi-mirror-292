# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: QueryMaxBuyingPowerRequest.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='QueryMaxBuyingPowerRequest.proto',
  package='',
  syntax='proto3',
  serialized_options=b'\n5com.huasheng.sa.quant.open.sdk.protobuf.trade.requestB\037QueryMaxBuyingPowerRequestProto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n QueryMaxBuyingPowerRequest.proto\"\x8e\x01\n\x1aQueryMaxBuyingPowerRequest\x12\x12\n\nmarketType\x18\x01 \x01(\t\x12\x11\n\tportfolio\x18\x02 \x01(\t\x12\x11\n\torderType\x18\x03 \x01(\t\x12\x12\n\norderPrice\x18\x04 \x01(\t\x12\x11\n\tstockCode\x18\x05 \x01(\t\x12\x0f\n\x07orderId\x18\x06 \x01(\tBX\n5com.huasheng.sa.quant.open.sdk.protobuf.trade.requestB\x1fQueryMaxBuyingPowerRequestProtob\x06proto3'
)




_QUERYMAXBUYINGPOWERREQUEST = _descriptor.Descriptor(
  name='QueryMaxBuyingPowerRequest',
  full_name='QueryMaxBuyingPowerRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='marketType', full_name='QueryMaxBuyingPowerRequest.marketType', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='portfolio', full_name='QueryMaxBuyingPowerRequest.portfolio', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='orderType', full_name='QueryMaxBuyingPowerRequest.orderType', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='orderPrice', full_name='QueryMaxBuyingPowerRequest.orderPrice', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='stockCode', full_name='QueryMaxBuyingPowerRequest.stockCode', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='orderId', full_name='QueryMaxBuyingPowerRequest.orderId', index=5,
      number=6, type=9, cpp_type=9, label=1,
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
  serialized_start=37,
  serialized_end=179,
)

DESCRIPTOR.message_types_by_name['QueryMaxBuyingPowerRequest'] = _QUERYMAXBUYINGPOWERREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

QueryMaxBuyingPowerRequest = _reflection.GeneratedProtocolMessageType('QueryMaxBuyingPowerRequest', (_message.Message,), {
  'DESCRIPTOR' : _QUERYMAXBUYINGPOWERREQUEST,
  '__module__' : 'QueryMaxBuyingPowerRequest_pb2'
  # @@protoc_insertion_point(class_scope:QueryMaxBuyingPowerRequest)
  })
_sym_db.RegisterMessage(QueryMaxBuyingPowerRequest)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
