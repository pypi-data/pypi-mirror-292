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


class GetMaxRetransmitSlot(Method[Response[UInt64]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Get the max slot seen from retransmit stage.

        #### Configuration Parameters Accepted:"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[UInt64],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.MAX_RETRANSMIT_SLOT
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        return { **request, "params": self.add_configuration(parameters) }

