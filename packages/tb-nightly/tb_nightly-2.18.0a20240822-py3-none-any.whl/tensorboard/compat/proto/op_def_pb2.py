# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorboard/compat/proto/op_def.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tensorboard.compat.proto import attr_value_pb2 as tensorboard_dot_compat_dot_proto_dot_attr__value__pb2
from tensorboard.compat.proto import full_type_pb2 as tensorboard_dot_compat_dot_proto_dot_full__type__pb2
from tensorboard.compat.proto import resource_handle_pb2 as tensorboard_dot_compat_dot_proto_dot_resource__handle__pb2
from tensorboard.compat.proto import types_pb2 as tensorboard_dot_compat_dot_proto_dot_types__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%tensorboard/compat/proto/op_def.proto\x12\x0btensorboard\x1a)tensorboard/compat/proto/attr_value.proto\x1a(tensorboard/compat/proto/full_type.proto\x1a.tensorboard/compat/proto/resource_handle.proto\x1a$tensorboard/compat/proto/types.proto\"\xfc\x06\n\x05OpDef\x12\x0c\n\x04name\x18\x01 \x01(\t\x12,\n\tinput_arg\x18\x02 \x03(\x0b\x32\x19.tensorboard.OpDef.ArgDef\x12-\n\noutput_arg\x18\x03 \x03(\x0b\x32\x19.tensorboard.OpDef.ArgDef\x12\x16\n\x0e\x63ontrol_output\x18\x14 \x03(\t\x12(\n\x04\x61ttr\x18\x04 \x03(\x0b\x32\x1a.tensorboard.OpDef.AttrDef\x12/\n\x0b\x64\x65precation\x18\x08 \x01(\x0b\x32\x1a.tensorboard.OpDeprecation\x12\x0f\n\x07summary\x18\x05 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x06 \x01(\t\x12\x16\n\x0eis_commutative\x18\x12 \x01(\x08\x12\x14\n\x0cis_aggregate\x18\x10 \x01(\x08\x12\x13\n\x0bis_stateful\x18\x11 \x01(\x08\x12\"\n\x1a\x61llows_uninitialized_input\x18\x13 \x01(\x08\x12$\n\x1cis_distributed_communication\x18\x15 \x01(\x08\x1a\x9f\x02\n\x06\x41rgDef\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12#\n\x04type\x18\x03 \x01(\x0e\x32\x15.tensorboard.DataType\x12\x11\n\ttype_attr\x18\x04 \x01(\t\x12\x13\n\x0bnumber_attr\x18\x05 \x01(\t\x12\x16\n\x0etype_list_attr\x18\x06 \x01(\t\x12\x43\n\x0bhandle_data\x18\x07 \x03(\x0b\x32..tensorboard.ResourceHandleProto.DtypeAndShape\x12\x0e\n\x06is_ref\x18\x10 \x01(\x08\x12\x38\n\x16\x65xperimental_full_type\x18\x11 \x01(\x0b\x32\x18.tensorboard.FullTypeDef\x1a\xbf\x01\n\x07\x41ttrDef\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\x12-\n\rdefault_value\x18\x03 \x01(\x0b\x32\x16.tensorboard.AttrValue\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\t\x12\x13\n\x0bhas_minimum\x18\x05 \x01(\x08\x12\x0f\n\x07minimum\x18\x06 \x01(\x03\x12.\n\x0e\x61llowed_values\x18\x07 \x01(\x0b\x32\x16.tensorboard.AttrValue\"5\n\rOpDeprecation\x12\x0f\n\x07version\x18\x01 \x01(\x05\x12\x13\n\x0b\x65xplanation\x18\x02 \x01(\t\"(\n\x06OpList\x12\x1e\n\x02op\x18\x01 \x03(\x0b\x32\x12.tensorboard.OpDefB{\n\x18org.tensorflow.frameworkB\x0bOpDefProtosP\x01ZMgithub.com/tensorflow/tensorflow/tensorflow/go/core/framework/op_def_go_proto\xf8\x01\x01\x62\x06proto3')



_OPDEF = DESCRIPTOR.message_types_by_name['OpDef']
_OPDEF_ARGDEF = _OPDEF.nested_types_by_name['ArgDef']
_OPDEF_ATTRDEF = _OPDEF.nested_types_by_name['AttrDef']
_OPDEPRECATION = DESCRIPTOR.message_types_by_name['OpDeprecation']
_OPLIST = DESCRIPTOR.message_types_by_name['OpList']
OpDef = _reflection.GeneratedProtocolMessageType('OpDef', (_message.Message,), {

  'ArgDef' : _reflection.GeneratedProtocolMessageType('ArgDef', (_message.Message,), {
    'DESCRIPTOR' : _OPDEF_ARGDEF,
    '__module__' : 'tensorboard.compat.proto.op_def_pb2'
    # @@protoc_insertion_point(class_scope:tensorboard.OpDef.ArgDef)
    })
  ,

  'AttrDef' : _reflection.GeneratedProtocolMessageType('AttrDef', (_message.Message,), {
    'DESCRIPTOR' : _OPDEF_ATTRDEF,
    '__module__' : 'tensorboard.compat.proto.op_def_pb2'
    # @@protoc_insertion_point(class_scope:tensorboard.OpDef.AttrDef)
    })
  ,
  'DESCRIPTOR' : _OPDEF,
  '__module__' : 'tensorboard.compat.proto.op_def_pb2'
  # @@protoc_insertion_point(class_scope:tensorboard.OpDef)
  })
_sym_db.RegisterMessage(OpDef)
_sym_db.RegisterMessage(OpDef.ArgDef)
_sym_db.RegisterMessage(OpDef.AttrDef)

OpDeprecation = _reflection.GeneratedProtocolMessageType('OpDeprecation', (_message.Message,), {
  'DESCRIPTOR' : _OPDEPRECATION,
  '__module__' : 'tensorboard.compat.proto.op_def_pb2'
  # @@protoc_insertion_point(class_scope:tensorboard.OpDeprecation)
  })
_sym_db.RegisterMessage(OpDeprecation)

OpList = _reflection.GeneratedProtocolMessageType('OpList', (_message.Message,), {
  'DESCRIPTOR' : _OPLIST,
  '__module__' : 'tensorboard.compat.proto.op_def_pb2'
  # @@protoc_insertion_point(class_scope:tensorboard.OpList)
  })
_sym_db.RegisterMessage(OpList)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\030org.tensorflow.frameworkB\013OpDefProtosP\001ZMgithub.com/tensorflow/tensorflow/tensorflow/go/core/framework/op_def_go_proto\370\001\001'
  _OPDEF._serialized_start=226
  _OPDEF._serialized_end=1118
  _OPDEF_ARGDEF._serialized_start=637
  _OPDEF_ARGDEF._serialized_end=924
  _OPDEF_ATTRDEF._serialized_start=927
  _OPDEF_ATTRDEF._serialized_end=1118
  _OPDEPRECATION._serialized_start=1120
  _OPDEPRECATION._serialized_end=1173
  _OPLIST._serialized_start=1175
  _OPLIST._serialized_end=1215
# @@protoc_insertion_point(module_scope)
