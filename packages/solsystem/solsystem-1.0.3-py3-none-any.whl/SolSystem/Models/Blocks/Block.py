from typing import Self, Any
from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
    Field,
)
from SolSystem.Models.Common import (
    Int64,
    UInt64,
    Lamports,
    Base58Str,
)
from SolSystem.Models.Transactions import (
    JsonTransaction,
    EncodedTransaction,
    Reward,
)



class Block(BaseModel):
    """### Summary
    Returns identity and transaction information about a confirmed block in the 
    ledger. For more information see 
    [solana documentation](https://solana.com/docs/rpc/json-structures#transactions)
    
    ### Parameters
    `block_height:` The number of blocks beneath this block

    `block_time:` Estimated production time, as Unix timestamp (seconds since
    the Unix epoch). null if not available

    `block_hash:` The blockhash of this block, as base-58 encoded string

    `parent_slot:` The slot index of this block's parent

    `previous_block_hash:` The blockhash of this block's parent, as base-58
    encoded string; if the parent block is not available due to ledger cleanup,
    this field will return "11111111111111111111111111111111"

    `transactions:` Present if "full" transaction details are requested

    `signatures:` Present if "signatures" are requested for transaction details;
    an array of signatures strings, corresponding to the transaction order in
    the block

    `rewards:` Block-level rewards, present if rewards are requested"""
    model_config = ConfigDict(alias_generator = to_camel, populate_by_name = True)

    block_height: UInt64 | None = None
    block_time: Int64 | None = None
    blockhash: Base58Str
    parent_slot: UInt64
    previous_blockhash: Base58Str

    transactions: list[JsonTransaction | EncodedTransaction] | None = None
    signatures: list[Base58Str] | None = None
    rewards: list[Reward] | None = None



class BlockCommitment(BaseModel):
    """### Parameters
    `commitment:` array logging the amount of cluster stake in lamports that has
    voted on the block at each depth from 0 to MAX_LOCKOUT_HISTORY + 1 or null
    if unknown block

    `total_stake:` total active stake, in lamports, of the current epoch"""
    model_config = ConfigDict(alias_generator = to_camel, populate_by_name = True)
    
    commitement: list[Lamports] | None
    total_stake: int



class SlotRange(BaseModel):
    """### Parameters
    `first_slot:` first slot to return block production information for (inclusive)

    `last_slot:` last slot to return block production information for (inclusive).
    If parameter not provided, defaults to the highest slot"""
    model_config = ConfigDict(alias_generator = to_camel)

    first_slot: UInt64
    last_slot: UInt64 | None = None



class IdentityValue(BaseModel):
    model_config = ConfigDict(alias_generator = to_camel)
    
    leader_slots: int
    blocks_produced: int

    @model_validator(mode = "before")
    @classmethod
    def from_list(cls: Self, data: Any) -> Any:
        if isinstance(data, list):
            return {"leaderSlots": data[0], "blocksProduced": data[1]}
        return data
    


class BlockProduction(BaseModel):
    """### Parameters
    `by_identity:` a dictionary of validator identities. Value is a two element
    array containing the number of leader slots and the number of blocks produced.
    
    `range:` Block production slot range"""
    model_config = ConfigDict(alias_generator = to_camel)

    by_identity: dict[Base58Str, IdentityValue]
    slot_range: SlotRange = Field(alias = "range")



class LatestBlockhash(BaseModel):
    """### Parameters
    `blockhash:` Current blockhash

    `last_valid_block_height:` Last block height at which the blockhash will be
    valid"""
    model_config = ConfigDict(alias_generator = to_camel)

    blockhash: Base58Str
    last_valid_block_height: UInt64



class PrioritizationFee(BaseModel):
    """### Parameters
    `slot:` Slot in which the fee was observed

    `prioritization_fee:` The per-compute-unit fee paid by at least one
    successfully landed transaction, specified in increments of micro-lamports
    (0.000001 lamports)"""
    model_config = ConfigDict(alias_generator = to_camel)

    slot: UInt64
    prioritization_fee: UInt64
