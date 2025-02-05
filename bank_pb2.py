# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: bank.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'bank.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nbank.proto\":\n\x0e\x41\x63\x63ountRequest\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x14\n\x0c\x61\x63\x63ount_type\x18\x02 \x01(\t\"6\n\x0f\x41\x63\x63ountResponse\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"G\n\x0f\x42\x61lanceResponse\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x0f\n\x07\x62\x61lance\x18\x02 \x01(\x01\x12\x0f\n\x07message\x18\x03 \x01(\t\"4\n\x0e\x44\x65positRequest\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x0e\n\x06\x61mount\x18\x02 \x01(\x01\"5\n\x0fWithdrawRequest\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x0e\n\x06\x61mount\x18\x02 \x01(\x01\"C\n\x0fInterestRequest\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x1c\n\x14\x61nnual_interest_rate\x18\x02 \x01(\x01\"K\n\x13TransactionResponse\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0f\n\x07\x62\x61lance\x18\x03 \x01(\x01\x32\x95\x02\n\x0b\x42\x61nkService\x12\x32\n\rCreateAccount\x12\x0f.AccountRequest\x1a\x10.AccountResponse\x12/\n\nGetBalance\x12\x0f.AccountRequest\x1a\x10.BalanceResponse\x12\x30\n\x07\x44\x65posit\x12\x0f.DepositRequest\x1a\x14.TransactionResponse\x12\x32\n\x08Withdraw\x12\x10.WithdrawRequest\x1a\x14.TransactionResponse\x12;\n\x11\x43\x61lculateInterest\x12\x10.InterestRequest\x1a\x14.TransactionResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'bank_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ACCOUNTREQUEST']._serialized_start=14
  _globals['_ACCOUNTREQUEST']._serialized_end=72
  _globals['_ACCOUNTRESPONSE']._serialized_start=74
  _globals['_ACCOUNTRESPONSE']._serialized_end=128
  _globals['_BALANCERESPONSE']._serialized_start=130
  _globals['_BALANCERESPONSE']._serialized_end=201
  _globals['_DEPOSITREQUEST']._serialized_start=203
  _globals['_DEPOSITREQUEST']._serialized_end=255
  _globals['_WITHDRAWREQUEST']._serialized_start=257
  _globals['_WITHDRAWREQUEST']._serialized_end=310
  _globals['_INTERESTREQUEST']._serialized_start=312
  _globals['_INTERESTREQUEST']._serialized_end=379
  _globals['_TRANSACTIONRESPONSE']._serialized_start=381
  _globals['_TRANSACTIONRESPONSE']._serialized_end=456
  _globals['_BANKSERVICE']._serialized_start=459
  _globals['_BANKSERVICE']._serialized_end=736
# @@protoc_insertion_point(module_scope)
