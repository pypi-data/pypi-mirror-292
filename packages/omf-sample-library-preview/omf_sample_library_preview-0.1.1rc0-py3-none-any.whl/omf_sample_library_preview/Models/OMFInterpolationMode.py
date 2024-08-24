from __future__ import annotations

from enum import Enum


class OMFInterpolationMode(Enum):
    Continuous = 'Continuous'
    Discrete = 'Discrete'
    StepwiseContinuousLeading = 'StepwiseContinuousLeading'
    StepwiseContinuousFollowing = 'StepwiseContinuousFollowing'
