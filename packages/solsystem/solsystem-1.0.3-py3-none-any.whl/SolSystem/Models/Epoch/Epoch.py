from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
)
from SolSystem.Models.Common import UInt64



class EpochInfo(BaseModel):
    """### Parameters
    `absolute_slot:` The current slot

    `block_height:` The current Block Height

    `epoch:` The current Epoch

    `slot_index:` The current slot relative to the start of the current epoch

    `slots_in_epoch:` The number of slots in this epoch

    `transaction_count:` Total number of transactions processed without error
    since genesis"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    absolute_slot: UInt64
    block_height: UInt64
    epoch: UInt64
    slot_index: UInt64
    slots_in_epoch: UInt64
    transaction_count: UInt64 | None = None



class EpochSchedule(BaseModel):
    """### Parameters
    `slots_per_epoch:` The maximum number of slots in each epoch

    `leader_schedule_slot_offset:` The number of slots before beginning of an
    epoch to calculate a leader schedule for that epoch

    `warmup:` Whether epochs start short and grow

    `first_normal_epoch:` First normal-length epoch,
    log2(slotsPerEpoch) - log2(MINIMUM_SLOTS_PER_EPOCH)

    `first_normal_slot:` MINIMUM_SLOTS_PER_EPOCH * (2.pow(firstNormalEpoch) - 1)"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    slots_per_epoch: UInt64
    leader_schedule_slot_offset: UInt64
    warmup: bool
    first_normal_epoch: UInt64
    first_normal_slot: UInt64