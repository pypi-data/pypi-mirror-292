from __future__ import annotations

from .OMFData import OMFData
from .OMFLinkValue import OMFLinkValue


class OMFLinkData(OMFData):
    def __init__(self, Values: list[OMFLinkValue]):
        super().__init__[OMFLinkValue](Values, '__Link', None, None)
