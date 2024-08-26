import inspect
from typing import Literal, Any
from enum import StrEnum, auto
from pydantic.alias_generators import to_camel
from pydantic import (
    ConfigDict,
    BaseModel,
    Field,
    model_serializer,
    SerializerFunctionWrapHandler,
)
from SolSystem.Models.Common import UInt64


class DataSlice(BaseModel):
    """### Summary
    Request a slice of the accounts data represented as a byte-length and 
    byte-offset. Only available if base58, base64, and base64+zstd"""
    length: int
    offset: int



class Commitment(StrEnum):
    FINALIZED = auto()
    CONFIRMED = auto()
    PROCESSED = auto()



class Encoding(StrEnum):
    BASE58 = "base58"
    """Is slow and limited to less than 129 bytes of Account data."""

    BASE64 = "base64"
    """Will return base64 encoded data for Account data of any size."""

    BASE64ZSTD = "base64+zstd"
    """Compresses the Account data using Zstandard and base64-encodes the result."""

    JSONPARSED = "jsonParsed"
    """Encoding attempts to use program-specific state parsers to return more 
    human-readable and explicit account state data. If jsonParsed is requested
    but a parser cannot be found, the field falls back to base64 encoding,
    detectable when the data field is type string."""




class ConfigurationField(StrEnum):
    ENCODING = auto()
    MIN_CONTEXT_SLOT = auto()
    DATA_SLICE = auto()
    WITH_CONTEXT = auto()
    COMMITMENT = auto()
    MAX_SUPPORTED_TRANSACTION_VERSION = auto()



class Configuration(BaseModel):
    """### Summary
    General Configuration object for requests. Some requests will only accept
    some of the listed parameters. In the event that you specify extraneous
    arguments, the relavent request will filter these out.
    
    ### Parameters
    `encoding:` Encoding format for the returned Account data
    
    `commitment:` Which state the node should query. When querying the
    ledger state, it's recommended to use lower levels of commitment to
    report progress and higher levels to ensure the state will not be
    rolled back.

    `min_context_slot:` The minimum slot that the request can be evaluated
    
    `withContext:` Wrap the result in an response context object.

    `data_slice:` Request a slice of the account's data. Data slicing is
    only available for base58, base64, or base64+zstd encodings.
    
    `max_supported_transaction_version:` The max transaction version to return
    in responses. If the requested block contains a transaction with a higher
    version, an error will be returned. If this parameter is omitted, only
    legacy transactions will be returned, and a block containing any versioned
    transaction will prompt the error."""
    model_config = ConfigDict(
        alias_generator = to_camel,
        extra = "allow",
        populate_by_name = True,
    )
    
    extra_fields: list[str] = Field(default_factory = list, exclude = True)

    encoding: Encoding | None = None
    min_context_slot: UInt64 | None = None
    data_slice: DataSlice | None = None
    with_context: bool | None = None
    commitment: Commitment | None = None
    max_supported_transaction_version: Literal["legacy", 0] | None = None


    def filter_for_accepted_parameters(
            self,
            accepts: list[ConfigurationField | str],
        ) -> None:
        """### Summary
        Only include the fields that the particular method accepts, also taking
        into account the extra fields added to this object."""
        attributes = list(inspect.signature(Configuration).parameters.keys())
        total_accepts = set(accepts).union(set(self.extra_fields))

        for attribute in attributes:
            if to_camel(attribute) not in total_accepts:
                setattr(self, attribute, None)
        
        attributes = list(inspect.signature(Configuration).parameters.keys())


    def add_extra_field(self, name: str, value: Any) -> None:
        """### Summary
        Add additional parameters to the configuration object to be included
        in the call. This allows flexibility for methods that have one off
        occuring arguments."""
        base_attributes = inspect.signature(Configuration).parameters.keys()
        if name in base_attributes:
            name = F"shadow__{name}"

        self.extra_fields.append(name)
        setattr(self, name, value)


    @model_serializer(mode = "wrap")
    def pre_serialize(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """### Summary
        When we have attributes that shadow existing attribute names they have
        a `shadow__` prefix appended to them. For serializing, we remove this
        prefix after calling the default serialization handler.
        
        For attributes added using the add_extra_field method, we must manually
        ensure their aliased name by calling `to_camel` on each."""
        def replace_shadowing(values: dict[str, Any]) -> dict:
            return {
                k.replace("shadow__", ""): (
                    replace_shadowing(v)
                    if isinstance(v, dict)
                    else v
                )
                for k,v in values.items()
            }
        
        def ensure_alias(values: dict[str, Any]) -> dict:
            return {
                (to_camel(k) if k in self.extra_fields else k): v
                for k,v in values.items()
            }
        return ensure_alias(
            values = replace_shadowing(values = handler(self))
        )
    
        