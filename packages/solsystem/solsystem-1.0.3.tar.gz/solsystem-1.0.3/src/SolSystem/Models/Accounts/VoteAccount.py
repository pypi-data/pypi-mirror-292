from typing import Any
from termcolor import colored
from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)
from SolSystem.Models.Common import (
    UInt64,
    Lamports,
    Base58Str,
)


class EpochCredit(BaseModel):
    """### Summary
    Earned credits data

    ### Parameters
    ```python
    epoch: UInt64
    credits: UInt64
    previous_credits: UInt64
    ```"""
    epoch: UInt64
    credits: UInt64
    previous_credits: UInt64


    @model_validator(mode = "before")
    @classmethod
    def pre_format_from_list(cls, value: list[Any]) -> dict[str, Any]:
        if len(value) != 3:
            raise ValueError(
                colored(
                    F"Expected a list of three elements, but got: {value}",
                    "light_red"
                )
            )
        return {
            "epoch": value[0],
            "credits": value[1],
            "previous_credits": value[2]
        }



class VoteAccount(BaseModel):
    """### Parameters
    `vote_pubkey:` Vote account address

    `node_pubkey:` Validator identity

    `activated_stake:` The stake, in lamports, delegated to this vote account
    and active in this epoch

    `epoch_vote_account:` Whether the vote account is staked for this epoch

    `commission:` Percentage (0-100) of rewards payout owed to the vote account

    `last_vote:` Most recent slot voted on by this vote account

    `epoch_credits:` Latest history of earned credits for up to five epochs, as
    an array of arrays containing: [epoch, credits, previousCredits]

    `root_slot:` Current root slot for this vote account"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )
    vote_pubkey: Base58Str
    node_pubkey: Base58Str
    activated_stake: Lamports
    epoch_vote_account: bool
    commission: float
    last_vote: UInt64
    epoch_credits: list[EpochCredit]
    root_slot: UInt64



class VoteAccounts(BaseModel):
    current: list[VoteAccount]
    delinquent: list[VoteAccount]
