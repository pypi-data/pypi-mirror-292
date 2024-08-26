"""### Summary
Methods related to inflation calculations.
Exports RPC Methods
- #### GetInflationGovernor
- #### GetInflationRate
- #### GetInflationReward
---
Exports Models
- #### InflationGovernor
- #### InflationRate
- #### InflationReward
"""
# Models
from .Inflation import (
    InflationGovernor,
    InflationRate,
    InflationReward,
)
# Methods
from .Methods.GetInflationGovernor import GetInflationGovernor
from .Methods.GetInflationRate import GetInflationRate
from .Methods.GetInflationReward import GetInflationReward


__all__ = [
    # Models
    "InflationGovernor",
    "InflationRate",
    "InflationReward",
    #Methods
    "GetInflationGovernor",
    "GetInflationRate",
    "GetInflationReward",
]