from __future__ import annotations

from enum import Enum


class OMFMessageType(Enum):
    """
    enum 0-2
    """

    Type = 'Type'
    Container = 'Container'
    Data = 'Data'
