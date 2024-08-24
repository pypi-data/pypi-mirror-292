from __future__ import annotations

from enum import Enum


class OMFMessageAction(Enum):
    """
    enum 0-2
    """

    Create = 'Create'
    Update = 'Update'
    Delete = 'Delete'
