from __future__ import annotations

from dataclasses import dataclass

from .OMFLinkSource import OMFLinkSource
from .OMFLinkTarget import OMFLinkTarget
from .Serializeable import Serializeable


@dataclass
class OMFLinkValue(Serializeable):
    Source: OMFLinkSource
    Target: OMFLinkTarget
