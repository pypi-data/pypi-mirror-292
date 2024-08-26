import base58
import base64
from typing import Self
from termcolor import colored
from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
    NonNegativeInt,
    model_validator,
    model_serializer,
)
from SolSystem.Models.Common import (
    UInt64,
    Encoding,
)


type Filter = MemcmpFilter | DataSizeFilter
"""### Summary
Filters available for certain requests. NOTE this is only for type hinting. Use
one of the specific Filter constructors for requests. More information can be
found in the [solana documentation](https://solana.com/docs/rpc#filter-criteria)"""



class MemcmpFilter(BaseModel):
    """### Summary
    Compares a provided series of bytes with program account data at a
    particular offset.
    
    ### Parameters
    `offset:` Offset into program account data to start comparison

    `bytes:` Data to match, as encoded string. Data is limited in size to 128
    or fewer decoded bytes.

    `encoding:` Encoding for filter bytes data, either "base58" or "base64".
    This field, and base64 support generally, is only available in solana-core
    v1.14.0 or newer. Please omit when querying nodes on earlier versions."""
    offset: NonNegativeInt
    bytes: str
    encoding: Encoding | None = None


    @model_validator(mode = "after")
    def validate_fields(self) -> Self:
        if self.encoding not in (Encoding.BASE58, Encoding.BASE64, None):
            raise ValueError(
                colored(
                    "Only base58 and base64 encoding is supported",
                    "light_red"
                )
            )
        if self.encoding == Encoding.BASE58:
            if len(base58.b58decode(self.bytes)) > 128:
                raise ValueError(
                    colored(
                        "Decoded bytes must be no longer than 128 in size",
                        "light_red"
                    )
                )
        if self.encoding == Encoding.BASE64:
            if len(base64.b64decode(self.bytes)) > 128:
                raise ValueError(
                    colored(
                        "Decoded bytes must be no longer than 128 in size",
                        "light_red"
                    )
                )
        return self


    @model_serializer()
    def prepare_output(self) -> dict:
        output = {
            "memcmp": {
                "offset": self.offset,
                "bytes": self.bytes
            }
        }
        if self.encoding:
            output["memcmp"].update({"encoding": self.encoding})
        return output
    


class DataSizeFilter(BaseModel):
    """### Summary
    Compares the program account data length with the provided data size"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )
    data_size: UInt64
