from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Nodes.Nodes import ClusterNode
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)



class GetClusterNodes(Method[Response[list[ClusterNode]]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns information about all the nodes participating in the cluster

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[list[ClusterNode]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.CLUSTER_NODES
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        
        return { **request, "params": self.add_configuration(parameters) }
