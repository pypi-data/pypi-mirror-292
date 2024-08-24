from __future__ import annotations

from enum import Enum


class OMFTypeCode(Enum):
    Null = 'Null'
    Array = 'Array'
    Boolean = 'Boolean'
    Integer = 'Integer'
    Number = 'Number'
    Object = 'Object'
    String = 'String'
