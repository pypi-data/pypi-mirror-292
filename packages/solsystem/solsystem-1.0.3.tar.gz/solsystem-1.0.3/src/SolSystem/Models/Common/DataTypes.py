from __future__ import annotations
import base58
import base64
from termcolor import colored
from typing import (
    Annotated,
    Any,
)
from pydantic import (
    Field,
    BaseModel,
    AfterValidator,
    model_validator,
    model_serializer,
)



def validate_public_key_encoding(key: str) -> str:
    assert len(base58.b58decode(key)) == 32, colored(
        F"Key '{key}' is not a valid base58 public key",
        "light_red"
    )
    return key
type PublicKey = Annotated[str, AfterValidator(validate_public_key_encoding)]
"""### Summary
A 32 byte base58 encoded solana public key"""



def validate_b58_encoding(data: str) -> str:
    assert base58.b58decode(data), colored(
        F"Data '{data}' is not a valid base58 encoded string",
        "light_red"
    )
    return data
type Base58Str = Annotated[str, AfterValidator(validate_b58_encoding)]
"""### Summary
Represents a base58 encoded string"""


def validate_b64_encoding(data: str) -> str:
    assert base64.b64decode(data), colored(
        F"Data '{data}' is not a valid base64 encoded string",
        "light_red"
    )
    return data
type Base64Str = Annotated[str, AfterValidator(validate_b64_encoding)]
"""### Summary
Represents a Base64 encoded string"""


def validate_signature_encoding(signature: str) -> str:
    assert len(base58.b58decode(signature)) == 64, colored(
        F"Signature '{signature}' is not a valid base58 signature",
        "light_red"
    )
    return signature
type Signature = Annotated[str, AfterValidator(validate_signature_encoding)]
"""### Summary
Represents a base58 encoded transaction signature"""


type Float64 = Annotated[
    float,
    Field(
        strict = True,
        gt = -1.7976931348623157E+308,
        lt = 1.7976931348623157E+308
    )
]


type UInt64 = Annotated[int, Field(strict = True, gt = -1, lt = 2**64)]
type Int64  = Annotated[int, Field(strict = True, gt = -2**63, lt = 2**63 - 1)]


type UInt32 = Annotated[int, Field(strict = True, gt = -1, lt = 2**32)]
type Int32  = Annotated[int, Field(strict = True, gt = -2**31, lt = 2**31 - 1)]


type UInt16 = Annotated[int, Field(strict = True, gt = -1, lt = 2**16)]
type Int16  = Annotated[int, Field(strict = True, gt = -2**15, lt = 2**15 - 1)]


type UInt8   = Annotated[int, Field(strict = True, gt = -1, lt = 2**8)]
type Int8    = Annotated[int, Field(strict = True, gt = -2**7, lt = 2**7 - 1)]



class Lamports(BaseModel):
    """### Summary
    Represents a balance of lamports and can convert easily to sol."""
    amount: int
    

    @staticmethod
    def per_sol() -> float:
        return 10**9
    

    @property
    def sol(self) -> float:
        if self.amount:
            return self.amount / 10**9
        return 0.0
    

    @model_validator(mode = "before")
    def format_input(cls, data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            return data
        return { "amount": data }
    

    @model_serializer()
    def serialize(self) -> int:
        return self.amount


    def __add__(self, other: Lamports) -> Lamports:
        return Lamports(amount = self.amount + other.amount)
    

    def __iadd__(self, other: Lamports) -> Lamports:
        return Lamports(amount = self.amount + other.amount)
    

    def __sub__(self, other: Lamports) -> Lamports:
        return Lamports(amount = self.amount - other.amount)
    

    def __mul__(self, other: Lamports | int | float) -> Lamports:
        if isinstance(other, Lamports):
            return Lamports(amount = self.amount * other.amount)
        return Lamports(amount = int(self.amount * other))


    def __truediv__(self, other: Lamports | int | float) -> float:
        if isinstance(other, Lamports):
            return self.amount / other.amount
        return self.amount / other
    

    def __floordiv__(self, other: Lamports | int | float) -> int:
        if isinstance(other, Lamports):
            return self.amount // other.amount
        return int(self.amount // other)


    def __lt__(self, other: Lamports | int | float) -> bool:
        if isinstance(other, Lamports):
            return self.amount < other.amount
        return self.amount < other


    def __le__(self, other: Lamports | int | float) -> bool:
        if isinstance(other, Lamports):
            return self.amount <= other.amount
        return self.amount <= other
    

    def __gt__(self, other: Lamports | int | float) -> bool:
        if isinstance(other, Lamports):
            return self.amount > other.amount
        return self.amount > other
        

    def __ge__(self, other: Lamports | int | float) -> bool:
        if isinstance(other, Lamports):
            return self.amount >= other.amount
        return self.amount >= other
    

    def __ne__(self, other: object) -> bool:
        if isinstance(other, Lamports):
            return self.amount != other.amount
        return self.amount != other
    
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Lamports):
            return self.amount == other.amount
        return self.amount == other
    
    
    def __abs__(self) -> Lamports:
        return Lamports(amount = abs(self.amount))
