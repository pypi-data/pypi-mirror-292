# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: UnLockTradeResponse.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='UnLockTradeResponse.proto',
  package='',
  syntax='proto3',
  serialized_options=b'\n6com.huasheng.sa.quant.open.sdk.protobuf.trade.responseB\030UnLockTradeResponseProto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x19UnLockTradeResponse.proto\"&\n\x13UnLockTradeResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x42R\n6com.huasheng.sa.quant.open.sdk.protobuf.trade.responseB\x18UnLockTradeResponseProtob\x06proto3'
)




_UNLOCKTRADERESPONSE = _descriptor.Descriptor(
  name='UnLockTradeResponse',
  full_name='UnLockTradeResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='UnLockTradeResponse.success', index=0,
      number=1, type=8, cpp_type=7, label=1,
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
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=29,
  serialized_end=67,
)

DESCRIPTOR.message_types_by_name['UnLockTradeResponse'] = _UNLOCKTRADERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

UnLockTradeResponse = _reflection.GeneratedProtocolMessageType('UnLockTradeResponse', (_message.Message,), {
  'DESCRIPTOR' : _UNLOCKTRADERESPONSE,
  '__module__' : 'UnLockTradeResponse_pb2'
  # @@protoc_insertion_point(class_scope:UnLockTradeResponse)
  })
_sym_db.RegisterMessage(UnLockTradeResponse)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
