# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: PushunsubscribeRequest.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='PushunsubscribeRequest.proto',
  package='',
  syntax='proto3',
  serialized_options=b'\n2com.huasheng.sa.quant.open.sdk.protobuf.hq.requestB\033PushunsubscribeRequestProto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1cPushunsubscribeRequest.proto\"?\n\x16PushunsubscribeRequest\x12\x0f\n\x07topicId\x18\x01 \x01(\t\x12\x14\n\x0crelatedParam\x18\x02 \x01(\tBQ\n2com.huasheng.sa.quant.open.sdk.protobuf.hq.requestB\x1bPushunsubscribeRequestProtob\x06proto3'
)




_PUSHUNSUBSCRIBEREQUEST = _descriptor.Descriptor(
  name='PushunsubscribeRequest',
  full_name='PushunsubscribeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='topicId', full_name='PushunsubscribeRequest.topicId', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='relatedParam', full_name='PushunsubscribeRequest.relatedParam', index=1,
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
  serialized_start=32,
  serialized_end=95,
)

DESCRIPTOR.message_types_by_name['PushunsubscribeRequest'] = _PUSHUNSUBSCRIBEREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

PushunsubscribeRequest = _reflection.GeneratedProtocolMessageType('PushunsubscribeRequest', (_message.Message,), {
  'DESCRIPTOR' : _PUSHUNSUBSCRIBEREQUEST,
  '__module__' : 'PushunsubscribeRequest_pb2'
  # @@protoc_insertion_point(class_scope:PushunsubscribeRequest)
  })
_sym_db.RegisterMessage(PushunsubscribeRequest)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
