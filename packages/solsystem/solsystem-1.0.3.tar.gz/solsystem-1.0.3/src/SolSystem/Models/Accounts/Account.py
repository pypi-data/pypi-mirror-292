from typing import Literal
from pydantic import (
    Field,
    BaseModel,
    field_validator,
)
from SolSystem.Models.Common import (
    UInt64,
    Encoding,
    Lamports,
    PublicKey,
)



class ValueData(BaseModel):
    data: str
    encoding: Encoding



class ReturnAccounts(BaseModel):
    addresses: list[PublicKey]
    encoding: Encoding



class Account(BaseModel):
    """### Parameters
    `data:` Data associated with the account, either as encoded binary data or
    JSON format {<program>: <state>} - depending on encoding parameter

    `executable:` Indicates if the account contains a program (and is strictly
    read-only)

    `lamports:` Number of lamports assigned to this account

    `owner:` Pubkey of the program this account has been assigned to

    `rent_epoch:` The epoch at which this account will next owe rent

    `space:` The data size of the account"""
    data: ValueData | str | dict | None
    executable: bool
    lamports: Lamports
    owner: PublicKey
    rent_epoch: UInt64 = Field(alias = "rentEpoch")
    space: UInt64


    @field_validator("data", mode = "before")
    @classmethod
    def prepare_data_field(cls, v: dict | list | Literal[""]) -> ValueData | str | dict | None:
        """### Summary
        We pre-format the value field because it can be either a list or a 
        dictionary. Also when empty, the data field can just be an empty string
        which we will treat as null. 
        
        There is a spcial case when th data does not fit into the requested 
        encoding in which case an error string is returned instead of the data."""
        if isinstance(v, list):
            return ValueData(** {"data": v[0], "encoding": v[1]})
        if "error" in v:
            return v
        if v == "":
            return None
        return v
    


class ProgramAccount(BaseModel):
    """### Parameters
    `pubkey:` The public key of the program account

    `account:` The account data. Fields are the same as `Account`"""
    pubkey: PublicKey
    account: Account