"""### Summary
Methods related to Solana Epochs and Schedule.
Exports RPC Methods:
- #### GetEpochInfo
- #### GetEpochSchedule
---
Exports RPC Models:
- #### EpochInfo
- #### EpochSchedule
"""
# Models
from .Epoch import (
    EpochInfo,
    EpochSchedule,
)
# Methods
from .Methods.GetEpochInfo import GetEpochInfo
from .Methods.GetEpochSchedule import GetEpochSchedule


__all__ = [
    # Models
    "EpochInfo",
    "EpochSchedule",
    # Methhods
    "GetEpochInfo",
    "GetEpochSchedule",
]