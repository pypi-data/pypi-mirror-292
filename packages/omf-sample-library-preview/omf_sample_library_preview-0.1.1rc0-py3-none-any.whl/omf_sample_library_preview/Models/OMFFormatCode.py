from __future__ import annotations

from enum import Enum


class OMFFormatCode(Enum):
    Int64 = 'Int64'
    Int32 = 'Int32'
    Int16 = 'Int16'
    Uint64 = 'Uint64'
    Uint32 = 'Uint32'
    Uint16 = 'Uint16'
    Float64 = 'Float64'
    Float32 = 'Float32'
    Float16 = 'Float16'
    Dictionary = 'Dictionary'
    DateTime = 'Date-Time'
