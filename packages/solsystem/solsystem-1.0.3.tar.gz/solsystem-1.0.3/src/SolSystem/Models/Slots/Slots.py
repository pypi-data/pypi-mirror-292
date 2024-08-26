from pydantic import BaseModel
from SolSystem.Models.Common import UInt64
    


class SnapshotSlot(BaseModel):
    """### Parameters
    `full:` Highest full snapshot slot

    `incremental:` Highest incremental snapshot slot based on full"""
    full: UInt64
    incremental: UInt64 | None = None
    