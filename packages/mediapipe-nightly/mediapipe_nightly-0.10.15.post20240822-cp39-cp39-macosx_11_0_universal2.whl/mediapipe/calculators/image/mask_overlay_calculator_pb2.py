# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mediapipe/calculators/image/mask_overlay_calculator.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from mediapipe.framework import calculator_pb2 as mediapipe_dot_framework_dot_calculator__pb2
try:
  mediapipe_dot_framework_dot_calculator__options__pb2 = mediapipe_dot_framework_dot_calculator__pb2.mediapipe_dot_framework_dot_calculator__options__pb2
except AttributeError:
  mediapipe_dot_framework_dot_calculator__options__pb2 = mediapipe_dot_framework_dot_calculator__pb2.mediapipe.framework.calculator_options_pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n9mediapipe/calculators/image/mask_overlay_calculator.proto\x12\tmediapipe\x1a$mediapipe/framework/calculator.proto\"\xf5\x01\n\x1cMaskOverlayCalculatorOptions\x12N\n\x0cmask_channel\x18\x01 \x01(\x0e\x32\x33.mediapipe.MaskOverlayCalculatorOptions.MaskChannel:\x03RED\".\n\x0bMaskChannel\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x07\n\x03RED\x10\x01\x12\t\n\x05\x41LPHA\x10\x02\x32U\n\x03\x65xt\x12\x1c.mediapipe.CalculatorOptions\x18\x82\xe0\x9cx \x01(\x0b\x32\'.mediapipe.MaskOverlayCalculatorOptions')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mediapipe.calculators.image.mask_overlay_calculator_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MASKOVERLAYCALCULATOROPTIONS']._serialized_start=111
  _globals['_MASKOVERLAYCALCULATOROPTIONS']._serialized_end=356
  _globals['_MASKOVERLAYCALCULATOROPTIONS_MASKCHANNEL']._serialized_start=223
  _globals['_MASKOVERLAYCALCULATOROPTIONS_MASKCHANNEL']._serialized_end=269
# @@protoc_insertion_point(module_scope)
