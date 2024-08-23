# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/type/calendar_period.proto
"""Generated protocol buffer code."""
from opensafely._vendor.google.protobuf.internal import enum_type_wrapper
from opensafely._vendor.google.protobuf import descriptor as _descriptor
from opensafely._vendor.google.protobuf import descriptor_pool as _descriptor_pool
from opensafely._vendor.google.protobuf import message as _message
from opensafely._vendor.google.protobuf import reflection as _reflection
from opensafely._vendor.google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b"\n!google/type/calendar_period.proto\x12\x0bgoogle.type*\x7f\n\x0e\x43\x61lendarPeriod\x12\x1f\n\x1b\x43\x41LENDAR_PERIOD_UNSPECIFIED\x10\x00\x12\x07\n\x03\x44\x41Y\x10\x01\x12\x08\n\x04WEEK\x10\x02\x12\r\n\tFORTNIGHT\x10\x03\x12\t\n\x05MONTH\x10\x04\x12\x0b\n\x07QUARTER\x10\x05\x12\x08\n\x04HALF\x10\x06\x12\x08\n\x04YEAR\x10\x07\x42x\n\x0f\x63om.google.typeB\x13\x43\x61lendarPeriodProtoP\x01ZHgoogle.golang.org/genproto/googleapis/type/calendarperiod;calendarperiod\xa2\x02\x03GTPb\x06proto3"
)

_CALENDARPERIOD = DESCRIPTOR.enum_types_by_name["CalendarPeriod"]
CalendarPeriod = enum_type_wrapper.EnumTypeWrapper(_CALENDARPERIOD)
CALENDAR_PERIOD_UNSPECIFIED = 0
DAY = 1
WEEK = 2
FORTNIGHT = 3
MONTH = 4
QUARTER = 5
HALF = 6
YEAR = 7


if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"\n\017com.google.typeB\023CalendarPeriodProtoP\001ZHgoogle.golang.org/genproto/googleapis/type/calendarperiod;calendarperiod\242\002\003GTP"
    _CALENDARPERIOD._serialized_start = 50
    _CALENDARPERIOD._serialized_end = 177
# @@protoc_insertion_point(module_scope)
