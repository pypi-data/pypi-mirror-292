from enum import StrEnum, auto
from pydantic import BaseModel
from SolSystem.Models.Common import UInt64



class StakeState(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()
    ACTIVATING = auto()
    DEACTIVATING = auto()



class StakeActivation(BaseModel):
    """### Parameters
    `state:` The stake account's activation state
    
    `active:` stake active during the epoch

    `inactive:` stake inactive during the epoch"""
    state: StakeState
    active: UInt64
    inactive: UInt64

