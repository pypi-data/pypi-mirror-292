from __future__ import annotations

from dataclasses import dataclass

from .OMFEnumValue import OMFEnumValue
from .OMFFormatCode import OMFFormatCode
from .OMFTypeCode import OMFTypeCode
from .Serializeable import Serializeable


@dataclass
class OMFEnum(Serializeable):
    Values: list[OMFEnumValue]
    Type: OMFTypeCode = None
    Format: OMFFormatCode = None
