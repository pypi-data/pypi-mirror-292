from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .OMFExtrapolationMode import OMFExtrapolationMode
from .Serializeable import Serializeable


@dataclass
class OMFContainer(Serializeable):
    Id: str
    TypeId: str
    Name: str = None
    Description: str = None
    Datasource: str = None
    Tags: list[str] = None
    Metadata: dict[str, Any] = None
    Indexes: list[str] = None
    Extrapolation: OMFExtrapolationMode = None
    PropertyOverrides: str = None

    def __hash__(self):
        return hash(self.Id)
