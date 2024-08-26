from typing import Any, Literal
from pydantic import model_serializer
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)


class GetNodeHealth(Method[Response[Literal["ok"]]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the current health of the node. A healthy node is one that is
        within HEALTH_CHECK_SLOT_DISTANCE slots of the latest cluster confirmed
        slot.

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[Literal["ok"]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.HEALTH
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
    
        return { **request, "params": self.add_configuration(parameters) }

