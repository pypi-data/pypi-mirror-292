# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: QueryPortfolioListResponse.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

from hs.common.pb.trade.vo import Portfolio_pb2 as trade_dot_vo_dot_Portfolio__pb2

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor.FileDescriptor(
  name='QueryPortfolioListResponse.proto',
  package='',
  syntax='proto3',
  serialized_options=b'\n6com.huasheng.sa.quant.open.sdk.protobuf.trade.responseB\037QueryPortfolioListResponseProto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n QueryPortfolioListResponse.proto\x1a\x18trade/vo/Portfolio.proto\"?\n\x1aQueryPortfolioListResponse\x12!\n\rportfolioList\x18\x01 \x03(\x0b\x32\n.PortfolioBY\n6com.huasheng.sa.quant.open.sdk.protobuf.trade.responseB\x1fQueryPortfolioListResponseProtob\x06proto3'
  ,
  dependencies=[trade_dot_vo_dot_Portfolio__pb2.DESCRIPTOR,])




_QUERYPORTFOLIOLISTRESPONSE = _descriptor.Descriptor(
  name='QueryPortfolioListResponse',
  full_name='QueryPortfolioListResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='portfolioList', full_name='QueryPortfolioListResponse.portfolioList', index=0,
      number=1, type=11, cpp_type=10, label=3,
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
  serialized_start=62,
  serialized_end=125,
)

_QUERYPORTFOLIOLISTRESPONSE.fields_by_name['portfolioList'].message_type = trade_dot_vo_dot_Portfolio__pb2._PORTFOLIO
DESCRIPTOR.message_types_by_name['QueryPortfolioListResponse'] = _QUERYPORTFOLIOLISTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

QueryPortfolioListResponse = _reflection.GeneratedProtocolMessageType('QueryPortfolioListResponse', (_message.Message,), {
  'DESCRIPTOR' : _QUERYPORTFOLIOLISTRESPONSE,
  '__module__' : 'QueryPortfolioListResponse_pb2'
  # @@protoc_insertion_point(class_scope:QueryPortfolioListResponse)
  })
_sym_db.RegisterMessage(QueryPortfolioListResponse)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
