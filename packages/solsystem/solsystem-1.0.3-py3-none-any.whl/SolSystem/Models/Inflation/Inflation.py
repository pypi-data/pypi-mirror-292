from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
)
from SolSystem.Models.Common import (
    UInt8,
    UInt64,
    Float64,
    Lamports,
)



class InflationGovernor(BaseModel):
    """### Parameters
    `initial:` The initial inflation percentage from time 0

    `terminal:` Terminal inflation percentage

    `taper:` Rate per year at which inflation is lowered. (Rate reduction is
    derived using the target slot time in genesis config)

    `foundation:` Percentage of total inflation allocated to the foundation

    `foundation_term:` Duration of foundation pool inflation in years"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    initial: Float64
    terminal: Float64
    taper: Float64
    foundation: Float64
    foundation_term: Float64



class InflationRate(BaseModel):
    """### Parameters
    `total:` The total inflation

    `validator:` Inflation allocated to validators

    `foundation:` Inflation allocated to the foundation

    `epoch:` Epoch for which these values are valid"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    total: Float64
    validator: Float64
    foundation: Float64
    epoch: UInt64



class InflationReward(BaseModel):
    """### Parameters
    `Epoch:` Epoch for which reward occured

    `effective_slot:` The slot in which the rewards are effective

    `amount:` Reward amount in lamports

    `post_balance:` Post balance of the account in lamports

    `commission:` Vote account commission when the reward was credited"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    epoch: UInt64
    effective_slot: UInt64
    amount: Lamports
    post_balance: Lamports
    commission: UInt8 | None = None
