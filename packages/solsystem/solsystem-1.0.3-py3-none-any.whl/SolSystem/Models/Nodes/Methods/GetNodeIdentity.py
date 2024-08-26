from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Nodes.Nodes import NodeIdentity
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)




class GetNodeIdentity(Method[Response[NodeIdentity]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns identity public key for the current node

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[NodeIdentity],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.IDENTITY
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
    
        return { **request, "params": self.add_configuration(parameters) }

