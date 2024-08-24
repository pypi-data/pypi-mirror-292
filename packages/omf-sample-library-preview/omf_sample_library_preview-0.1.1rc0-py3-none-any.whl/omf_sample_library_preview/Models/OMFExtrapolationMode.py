from __future__ import annotations

from enum import Enum


class OMFExtrapolationMode(Enum):
    All = 'All'
    _None = 'None'
    Forward = 'Forward'
    Backward = 'Backward'
