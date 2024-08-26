from __future__ import annotations
from typing import (
    Annotated,
    TypeVar,
    Generic,
    Any,
)
from enum import StrEnum
from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    AliasPath,
    ConfigDict,
    AliasChoices,
    StringConstraints,
    model_serializer,
    field_validator,
    Field,
)
from SolSystem.Models.Common import (
    UInt64,
    UInt32,
)



type RpcVersion = Annotated[
    str,
    StringConstraints(pattern = r"^\d{1,2}\.\d{1,2}$")
]
"""### Summary
Solana Rpc Version String

```python
type RpcVersion = Annotated[
    str,
    StringConstraints(pattern = r"^\\d{1,2}\\.\\d{1,2}$")
]
```"""


type ApiVersion = Annotated[
    str,
    StringConstraints(pattern = r"^\d{1,2}\.\d{1,2}\.\d{1,2}$")
]
"""### Summary
Solana RPC Api version string

```python
type ApiVersion = Annotated[
    str,
    StringConstraints(pattern = r"^\\d{1,2}\\.\\d{1,2}\\.\\d{1,2}$")
]
```"""


class RpcResponseContext(BaseModel):
    """### Summary
    Context metadata for an rpc respnse
    
    ### Properties
    ```python
    api_version: ApiVersion | None
    slot: UInt64
    ```"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True
    )
    api_version: ApiVersion | None = None
    slot: UInt64

    

class Error(BaseModel):
    code: int
    message: str
    data: Any | None = None



Result = TypeVar("Result")
class Response(BaseModel, Generic[Result]):
    """### Summary
    Generic response base class. All Solana API requests will return this
    response object with some context and some value result.
    
    ### Properties
    ```python
    jsonrpc: RpcVersion = "2.0"
    context: RpcResponseContext | None
    value: Result | None # Generic[Result]
    error: Error | None
    id: UInt32
    ```"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True
    )
    
    jsonrpc: RpcVersion = "2.0"
    context: RpcResponseContext | None = Field(
        default = None,
        validation_alias = AliasPath("result", "context")
    )
    value: Result | None = Field(
        default = None,
        validation_alias = AliasChoices(
            AliasPath("result", "value"),
            "result",
        )
    )
    error: Error | None = None
    id: UInt32


    @model_serializer()
    def serialize(self) -> dict[str, Any]:
        value = self.value
        if hasattr(self.value, "model_dump"):
            assert isinstance(self.value, BaseModel), "Value is not a pydantic model."
            value = self.value.model_dump()

        error = self.error
        if self.error:
            error = self.error.model_dump()

        result = value
        if self.context:
            result = {
                "context": self.context.model_dump(),
                "value": value
            }

        return {
            "jsonrpc": self.jsonrpc,
            "result": result,
            "error": error,
            "id": self.id
        }
    


class WsNotificationName(StrEnum):
    """### Summary
    When websocket methods send a notification, they specify a method name from
    this list."""
    ACCOUNT            = "accountNotification"
    BLOCK              = "blockNotification"
    LOGS               = "logsNotification"
    PROGRAM            = "programNotification"
    ROOT               = "rootNotification"
    SIGNATURE          = "signatureNotification"
    SLOT               = "slotNotification"
    SLOTS_UPDATE       = "slotsUpdatesNotification"
    VOTE               = "voteNotification"
    HELIUS_TRANSACTION = "transactionNotification"



class WsResponse(BaseModel, Generic[Result]):
    """### Summary
    Generic websocket response baseclass. The Result type will be determined
    by the method being called. Note, we use AliasPaths to reduce the nesting
    of response objects since, for now, this doesnt seem to effect anything
    and is there as just a design choice in the API.

    ### Properties
    ```python
    jsonrpc: RpcVersion
    method: WsNotificationName
    context: RpcResponseContext | None
    value: Result | None # Generic[Result]
    subscription: UInt64
    error: Error | None
    ```"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True
    )

    jsonrpc: RpcVersion = "2.0"
    method: WsNotificationName
    context: RpcResponseContext | None = Field(
        default = None,
        validation_alias = AliasPath("params", "result", "context")
    )
    value: Result = Field(
        validation_alias = AliasChoices(
            AliasPath("params", "result", "value"),
            AliasPath("params", "result"),
            "params",
        )
    )
    subscription: UInt64 = Field(
        validation_alias = AliasPath("params", "subscription")
    )


    @field_validator("value", mode = "before")
    @classmethod
    def simplify_value(cls, value: Any) -> dict:
        print(value)
        return value


    @model_serializer()
    def serialize(self) -> dict[str, Any]:
        value = self.value
        if hasattr(self.value, "model_dump"):
            assert isinstance(self.value, BaseModel), "Value is not a pydantic model."
            value = self.value.model_dump()

        result = value
        if self.context:
            result = {
                "context": self.context.model_dump(),
                "value": value
            }

        return {
            "jsonrpc": self.jsonrpc,
            "result": result,
            "subscription": self.subscription
        }
