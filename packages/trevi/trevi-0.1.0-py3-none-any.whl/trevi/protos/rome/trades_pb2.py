# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/rome/trades.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18protos/rome/trades.proto\x12\x0brome.trades\x1a\x1fgoogle/protobuf/timestamp.proto\"d\n\x0f\x45quityMarketBuy\x12\x0e\n\x06ticker\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x01\x12/\n\rtime_in_force\x18\x03 \x01(\x0e\x32\x18.rome.trades.TimeInForce\"e\n\x10\x45quityMarketSell\x12\x0e\n\x06ticker\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x01\x12/\n\rtime_in_force\x18\x03 \x01(\x0e\x32\x18.rome.trades.TimeInForce\"d\n\x0f\x43ryptoMarketBuy\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x01\x12/\n\rtime_in_force\x18\x03 \x01(\x0e\x32\x18.rome.trades.TimeInForce\"e\n\x10\x43ryptoMarketSell\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x01\x12/\n\rtime_in_force\x18\x03 \x01(\x0e\x32\x18.rome.trades.TimeInForce\"4\n\x10PortfolioDetails\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"\xf2\x02\n\x05Trade\x12-\n\ttimestamp\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x10\n\x08strategy\x18\x02 \x01(\t\x12\x30\n\tportfolio\x18\x03 \x01(\x0b\x32\x1d.rome.trades.PortfolioDetails\x12\x39\n\x11\x65quity_market_buy\x18\n \x01(\x0b\x32\x1c.rome.trades.EquityMarketBuyH\x00\x12;\n\x12\x65quity_market_sell\x18\x0b \x01(\x0b\x32\x1d.rome.trades.EquityMarketSellH\x00\x12\x39\n\x11\x63rypto_market_buy\x18\x0c \x01(\x0b\x32\x1c.rome.trades.CryptoMarketBuyH\x00\x12;\n\x12\x63rypto_market_sell\x18\r \x01(\x0b\x32\x1d.rome.trades.CryptoMarketSellH\x00\x42\x06\n\x04type\"_\n\nFilledItem\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x01\x12\r\n\x05price\x18\x03 \x01(\x01\x12\x0e\n\x06\x62roker\x18\n \x01(\t\x12\x10\n\x08trade_id\x18\x64 \x01(\t\"B\n\x06\x46illed\x12&\n\x05items\x18\x01 \x03(\x0b\x32\x17.rome.trades.FilledItem\x12\x10\n\x08trade_id\x18\x64 \x01(\t\"A\n\nPlacedItem\x12!\n\x05trade\x18\x01 \x01(\x0b\x32\x12.rome.trades.Trade\x12\x10\n\x08trade_id\x18\x64 \x01(\t\"B\n\x06Placed\x12&\n\x05items\x18\x01 \x03(\x0b\x32\x17.rome.trades.PlacedItem\x12\x10\n\x08trade_id\x18\x64 \x01(\t\"\x92\x01\n\x0bTradeUpdate\x12-\n\ttimestamp\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12%\n\x06placed\x18\n \x01(\x0b\x32\x13.rome.trades.PlacedH\x00\x12%\n\x06\x66illed\x18\x0b \x01(\x0b\x32\x13.rome.trades.FilledH\x00\x42\x06\n\x04type*>\n\x06Status\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0b\n\x07PENDING\x10\x01\x12\x0c\n\x08\x41PPROVED\x10\x02\x12\x0c\n\x08REJECTED\x10\x03*(\n\x0bTimeInForce\x12\x07\n\x03IOC\x10\x00\x12\x07\n\x03\x46OK\x10\x01\x12\x07\n\x03GTC\x10\x02\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.rome.trades_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_STATUS']._serialized_start=1360
  _globals['_STATUS']._serialized_end=1422
  _globals['_TIMEINFORCE']._serialized_start=1424
  _globals['_TIMEINFORCE']._serialized_end=1464
  _globals['_EQUITYMARKETBUY']._serialized_start=74
  _globals['_EQUITYMARKETBUY']._serialized_end=174
  _globals['_EQUITYMARKETSELL']._serialized_start=176
  _globals['_EQUITYMARKETSELL']._serialized_end=277
  _globals['_CRYPTOMARKETBUY']._serialized_start=279
  _globals['_CRYPTOMARKETBUY']._serialized_end=379
  _globals['_CRYPTOMARKETSELL']._serialized_start=381
  _globals['_CRYPTOMARKETSELL']._serialized_end=482
  _globals['_PORTFOLIODETAILS']._serialized_start=484
  _globals['_PORTFOLIODETAILS']._serialized_end=536
  _globals['_TRADE']._serialized_start=539
  _globals['_TRADE']._serialized_end=909
  _globals['_FILLEDITEM']._serialized_start=911
  _globals['_FILLEDITEM']._serialized_end=1006
  _globals['_FILLED']._serialized_start=1008
  _globals['_FILLED']._serialized_end=1074
  _globals['_PLACEDITEM']._serialized_start=1076
  _globals['_PLACEDITEM']._serialized_end=1141
  _globals['_PLACED']._serialized_start=1143
  _globals['_PLACED']._serialized_end=1209
  _globals['_TRADEUPDATE']._serialized_start=1212
  _globals['_TRADEUPDATE']._serialized_end=1358
# @@protoc_insertion_point(module_scope)
