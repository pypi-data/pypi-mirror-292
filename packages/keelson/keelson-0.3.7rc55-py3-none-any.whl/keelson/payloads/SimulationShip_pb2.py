# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: SimulationShip.proto
# Protobuf Python Version: 5.27.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    0,
    '',
    'SimulationShip.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14SimulationShip.proto\x12\x10keelson.compound\"\xf0\x03\n\x0eSimulationShip\x12\x0f\n\x07ship_id\x18\x01 \x01(\x05\x12\x14\n\x0clatitude_deg\x18\x02 \x01(\x02\x12\x15\n\rlongitude_deg\x18\x03 \x01(\x02\x12\x16\n\x0e\x61ltitude_meter\x18\x04 \x01(\x02\x12\x13\n\x0bheading_deg\x18\x05 \x01(\x02\x12\x1b\n\x13rate_of_turn_degmin\x18\x06 \x01(\x02\x12\x10\n\x08roll_deg\x18\x07 \x01(\x02\x12\x11\n\tpitch_deg\x18\x08 \x01(\x02\x12\x1b\n\x13longitudal_speed_ms\x18\t \x01(\x02\x12\x19\n\x11vertical_speed_ms\x18\n \x01(\x02\x12\x1d\n\x15vertical_bow_speed_ms\x18\x0b \x01(\x02\x12\x1f\n\x17vertical_stern_speed_ms\x18\x0c \x01(\x02\x12\x1e\n\x16\x63ourse_over_ground_deg\x18\r \x01(\x02\x12\x1f\n\x17speed_over_ground_knots\x18\x0e \x01(\x02\x12\x1e\n\x16wind_apparent_speed_ms\x18\x0f \x01(\x02\x12\x1f\n\x17wind_apparent_angle_deg\x18\x10 \x01(\x02\x12\x1a\n\x12wind_true_speed_ms\x18\x11 \x01(\x02\x12\x1b\n\x13wind_true_angle_deg\x18\x12 \x01(\x02\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'SimulationShip_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SIMULATIONSHIP']._serialized_start=43
  _globals['_SIMULATIONSHIP']._serialized_end=539
# @@protoc_insertion_point(module_scope)
