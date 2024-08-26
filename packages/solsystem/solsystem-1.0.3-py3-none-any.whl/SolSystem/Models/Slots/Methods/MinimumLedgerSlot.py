from typing import Any, Self
from pydantic import (
    Field,
    model_serializer,
)
from SolSystem.Models.Common import (
    UInt64,
    WsResponse,
    Method,
    MethodMetadata,
    RPCMethodName,
    Configuration,
)



class MinimumLedgerSlot(Method[WsResponse[UInt64]]):
    response_type: type = WsResponse[UInt64]
    metadata: MethodMetadata = Field(
        default = MethodMetadata(method = RPCMethodName.MINIMUM_LEDGER_SLOT),
        frozen = True,
    )


    def __init__(
            self: Self,
            configuration: Configuration = None,
        ) -> None:
        """### Summary
        Returns the lowest slot that the node has information about in its
        ledger.

        #### Configuration Parameters Accepted:"""
        if not configuration: configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(**{
            "configuration": configuration,
        })


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        
        if self.configuration:
            options = self.configuration.model_dump(exclude_none = True)
            if options:
                parameters.append(options)
        return { **request, "params": parameters }

