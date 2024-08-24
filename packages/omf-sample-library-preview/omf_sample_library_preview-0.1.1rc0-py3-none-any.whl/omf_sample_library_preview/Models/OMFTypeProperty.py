from __future__ import annotations

from dataclasses import dataclass

from .OMFFormatCode import OMFFormatCode
from .OMFInterpolationMode import OMFInterpolationMode
from .OMFTypeCode import OMFTypeCode
from .Serializeable import Serializeable


@dataclass
class OMFTypeProperty(Serializeable):
    Type: OMFTypeCode | list[OMFTypeCode] = None
    Format: OMFFormatCode = None
    Items: 'OMFTypeProperty' = None
    RefTypeId: str = None
    IsIndex: bool = None
    IsQuality: bool = None
    Name: str = None
    Description: str = None
    Uom: str = None
    Minimum: float | int = None
    Maximum: float | int = None
    Interpolation: OMFInterpolationMode = None
    AdditionalProperties: 'OMFTypeProperty' = None
