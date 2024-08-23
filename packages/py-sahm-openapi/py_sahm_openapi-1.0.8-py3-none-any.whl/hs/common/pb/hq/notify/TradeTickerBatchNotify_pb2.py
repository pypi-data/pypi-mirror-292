# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: TradeTickerBatchNotify.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

from hs.common.pb.hq.notify import TradeTickerItemNotify_pb2 as hq_dot_notify_dot_TradeTickerItemNotify__pb2

DESCRIPTOR = _descriptor.FileDescriptor(
  name='TradeTickerBatchNotify.proto',
  package='',
  syntax='proto3',
  serialized_options=b'\n1com.huasheng.sa.quant.open.sdk.protobuf.hq.notifyB\033TradeTickerBatchNotifyProto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1cTradeTickerBatchNotify.proto\x1a%hq/notify/TradeTickerItemNotify.proto\"~\n\x16TradeTickerBatchNotify\x12\x11\n\tstockCode\x18\x01 \x01(\t\x12\x39\n\x19tradeTickerItemNotifyList\x18\x02 \x03(\x0b\x32\x16.TradeTickerItemNotify\x12\x16\n\x0esourcePushTime\x18\x03 \x01(\x03\x42P\n1com.huasheng.sa.quant.open.sdk.protobuf.hq.notifyB\x1bTradeTickerBatchNotifyProtob\x06proto3'
  ,
  dependencies=[hq_dot_notify_dot_TradeTickerItemNotify__pb2.DESCRIPTOR,])




_TRADETICKERBATCHNOTIFY = _descriptor.Descriptor(
  name='TradeTickerBatchNotify',
  full_name='TradeTickerBatchNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='stockCode', full_name='TradeTickerBatchNotify.stockCode', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tradeTickerItemNotifyList', full_name='TradeTickerBatchNotify.tradeTickerItemNotifyList', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='sourcePushTime', full_name='TradeTickerBatchNotify.sourcePushTime', index=2,
      number=3, type=3, cpp_type=2, label=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=71,
  serialized_end=197,
)

_TRADETICKERBATCHNOTIFY.fields_by_name['tradeTickerItemNotifyList'].message_type = hq_dot_notify_dot_TradeTickerItemNotify__pb2._TRADETICKERITEMNOTIFY
DESCRIPTOR.message_types_by_name['TradeTickerBatchNotify'] = _TRADETICKERBATCHNOTIFY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TradeTickerBatchNotify = _reflection.GeneratedProtocolMessageType('TradeTickerBatchNotify', (_message.Message,), {
  'DESCRIPTOR' : _TRADETICKERBATCHNOTIFY,
  '__module__' : 'TradeTickerBatchNotify_pb2'
  # @@protoc_insertion_point(class_scope:TradeTickerBatchNotify)
  })
_sym_db.RegisterMessage(TradeTickerBatchNotify)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
