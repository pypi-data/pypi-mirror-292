from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .OMFClassification import OMFClassification
from .OMFEnum import OMFEnum
from .OMFExtrapolationMode import OMFExtrapolationMode
from .OMFTypeProperty import OMFTypeProperty
from .OMFTypeType import OMFTypeType
from .Serializeable import Serializeable


@dataclass
class OMFType(Serializeable):
    Id: str
    Classification: OMFClassification = None
    Type: OMFTypeType = None
    Version: str = None
    Name: str = None
    Description: str = None
    Tags: list[str] = None
    Metadata: dict[str, Any] = None
    Enum: OMFEnum = None
    Extrapolation: OMFExtrapolationMode = None
    Properties: dict[str, OMFTypeProperty] = None

    def __hash__(self):
        return hash(self.Id)
