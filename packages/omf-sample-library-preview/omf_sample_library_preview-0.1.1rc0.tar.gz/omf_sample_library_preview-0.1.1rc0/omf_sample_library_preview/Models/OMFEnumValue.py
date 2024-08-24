from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .Serializeable import Serializeable


@dataclass
class OMFEnumValue(Serializeable):
    Name: str
    Value: int | Any
