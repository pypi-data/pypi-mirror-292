from __future__ import annotations
from pydantic import (
    BaseModel,
    ConfigDict,
    model_serializer,
    field_validator,
)
from typing import Any, Literal
from pydantic.alias_generators import to_camel
from SolSystem.Models.Common import (
    WsMethod,
    PublicKey,
    Signature,
    WsResponse,
    WsMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class LogsAccountFilter(BaseModel):
    """### Summary
    
    Mentions is an array containing a single Pubkey and if present, subscribe
    to only transactions mentioning this address.
    
    NOTE The mentions field currently only supports one Pubkey string per method
    call. Listing additional addresses will result in an error."""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True
    )
    mentions: list[PublicKey]

    @field_validator("mentions", mode = "after")
    def restrict_mentions(cls, value: list[PublicKey]) -> list[PublicKey]:
        if len(value) > 1:
            raise ValueError("mentions is currently limited to 1 address.")
        return value



class LogsNotification(BaseModel):
    """### Summary
    Logs associated with a transaction or None if the transaction failed.
    If simulation failed before the transaction was able to execute (for example
    due to an invalid blockhash or signature verification failure) then
    transaction is also None."""
    signature: Signature
    err: dict | None = None
    block: list[str] | None = None



class WsGetLogs(WsMethod[WsResponse[LogsNotification]]):
    filter: Literal["all"] | Literal["allWithVotes"] | LogsAccountFilter

    def __init__(
            self,
            filter: Literal["all"] | Literal["allWithVotes"] | LogsAccountFilter = "all", 
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Subscribe to transaction logging.

        ### Parameters
        `filter:` All is subscribe to all transactions except for simple vote
        transactions. 

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = WsResponse[LogsNotification],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.LOGS),
            configuration = configuration,
            filter = filter, # type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.filter]
        return { **request, "params": self.add_configuration(parameters) }
