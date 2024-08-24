from __future__ import annotations

from dataclasses import dataclass

from .Serializeable import Serializeable


@dataclass
class OMFLinkSource(Serializeable):
    TypeId: str
    Index: str
