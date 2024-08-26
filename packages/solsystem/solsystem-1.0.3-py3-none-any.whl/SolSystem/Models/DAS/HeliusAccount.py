from __future__ import annotations
from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
)
from SolSystem.Models.Common import (
    UInt64,
    PublicKey,
)



class HeliusTokenAccounts(BaseModel):
    """### Summary
    A specific return type for the helius das method allowing us to fetch all
    token accounts for a mint.

    ### Parameters
    `total:` The total number of token accounts found for this mint/owner.

    `limit:` The maximum number of accounts requested.

    `cursor:` The pagination cursor. This field is omitted from the response
    when there is no further data.

    `token_accounts:` A list of helius token account objects returned."""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )
    total: UInt64
    limit: UInt64
    cursor: str | None = None
    token_accounts: list[HeliusTokenAccount]




class HeliusTokenAccount(BaseModel):
    """### Summary
    A slightly modified version of the standard TokenAccount return.
    
    ### Parameters
    `address:` The token account address owning these coins.
    
    `mint:` The mint account of a particular token.
    
    `owner:` The owning account for the token account
    
    `amount:` The owned amount of a token
    
    `delegated_amount:` The delegated amount.
    
    `frozen:` Whether the token account funds are frozen or not."""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    address: PublicKey
    mint: PublicKey
    owner: PublicKey
    amount: UInt64
    delegated_amount: UInt64
    frozen: bool
