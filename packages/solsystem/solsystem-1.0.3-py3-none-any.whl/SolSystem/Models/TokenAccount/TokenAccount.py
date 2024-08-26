from typing import Annotated
from pydantic import (
    BaseModel,
    ConfigDict,
    AfterValidator,
    Field,
)
from pydantic.alias_generators import to_camel
from SolSystem.Models.Common import PublicKey, UInt8
from SolSystem.Models.Accounts import Account



def validate_conversion(s: str):
    try: return str(int(s))
    except: return str(float(s))
type NumericString = Annotated[str, AfterValidator(validate_conversion)]



class TokenAmount(BaseModel):
    """### Parameters
    `amount:` Raw amount of tokens as a string, ignoring decimals.

    `decimals:` Number of decimals configured for token's mint.

    `ui_amount:` Token amount as a float, accounting for decimals. DEPRECATED

    `ui_amount_string:` Token amount as a string, accounting for decimals."""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )
    
    address: PublicKey | None = None
    amount: NumericString | None = None
    decimals: UInt8 | None = None
    ui_amount: float | None = Field(default = None, deprecated = True)
    ui_amount_string: NumericString | None = None



class TokenBalance(BaseModel):
    """### Summary
    A structure representing the token balance of one token on an account.
    
    ### Parameters:
    `account_index:` Index of the account in the parent object in which the
    token balance is provided for.
    
    `mint:` Pubkey of the token's mint.
    
    `owner:` Pubkey of token balance's owner.

    `program_id:` Pubkey of the Token program that owns the account.

    `ui_token_amount:` Oject representing token amount."""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    account_index: int
    mint: PublicKey
    owner: PublicKey | None = None
    program_id: PublicKey | None = None
    ui_token_amount: TokenAmount



class TokenAccount(BaseModel):
    """### Parameters
    `amount:` The raw balance without decimals, a string representation of u64

    `decimals:` Number of base 10 digits to the right of the decimal place

    `ui_amount:` DEPRECATE. The balance, using mint-prescribed decimals

    `ui_amount_string:` The balance as a string, using mint-prescribed decimals"""
    pubkey: PublicKey
    account: Account