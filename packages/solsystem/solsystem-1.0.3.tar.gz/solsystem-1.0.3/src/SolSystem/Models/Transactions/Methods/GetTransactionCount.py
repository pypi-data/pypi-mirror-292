from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)


class GetTransactionCount(Method[Response[UInt64]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the current Transaction count from the ledger.

        #### Configuration Parameters Accepted:
        `encoding`, `min_context_slot`"""
        if not configuration: configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[UInt64],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.TRANSACTION_COUNT
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
    
        return { **request, "params": self.add_configuration(parameters) }
