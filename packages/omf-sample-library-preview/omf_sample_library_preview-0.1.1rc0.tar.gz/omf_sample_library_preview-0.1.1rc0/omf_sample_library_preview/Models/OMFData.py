from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from .Serializeable import Serializeable

T = TypeVar('T')


@dataclass
class OMFData(Generic[T], Serializeable):
    Values: list[T]
    TypeId: str = None
    ContainerId: str = None
    Properties: dict[str, Any] = None
