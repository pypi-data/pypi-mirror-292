from __future__ import annotations
from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
)
from SolSystem.Models.Common import (
    UInt64,
    UInt16,
    Lamports,
    PublicKey,
)



class PerformanceSample(BaseModel):
    """### Parameters
    `slot:` Slot in which sample was taken at

    `num_transactions:` Number of transactions processed during the sample period

    `num_slots:` Number of slots completed during the sample period

    `sample_period_secs:` Number of seconds in a sample window

    `num_non_vote_transaction:` Number of non-vote transactions processed during
    the sample period.
    
    `num_voting_transactions:` Number of voting transactions processed during
    the sample period."""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    slot: UInt64
    num_transactions: UInt64
    num_slots: UInt64
    sample_period_secs: UInt16
    num_non_vote_transactions: UInt64

    @property
    def num_voting_transactions(self) -> UInt64:
        return self.num_transactions - self.num_non_vote_transactions



class Supply(BaseModel):
    """### Parameters
    `total:` Total supply in lamports

    `circulating:` Circulating supply in lamports

    `non_circulating:` Non-circulating supply in lamports

    `non_circulating_accounts:` an array of account addresses of non-circulating
    accounts, as strings. If excludeNonCirculatingAccountsList is enabled, the
    returned array will be empty."""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    total: Lamports
    circulating: Lamports
    non_circulating: Lamports
    non_circulating_accounts: list[PublicKey]