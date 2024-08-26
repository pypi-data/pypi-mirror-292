from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Nodes.Nodes import NodeVersion
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)


class GetNodeVersion(Method[Response[NodeVersion]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the current Solana version running on the node

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[NodeVersion],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.VERSION
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
    
        return { **request, "params": self.add_configuration(parameters) }

