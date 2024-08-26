from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)



class GetMinimumLedgerSlot(Method[Response[UInt64]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the lowest slot that the node has information about in its
        ledger.

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[UInt64],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.MINIMUM_LEDGER_SLOT
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        return { **request, "params": self.add_configuration(parameters) }

