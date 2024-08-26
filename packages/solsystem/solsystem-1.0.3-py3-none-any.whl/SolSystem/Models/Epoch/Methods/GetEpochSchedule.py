from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Epoch.Epoch import EpochSchedule
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)


class GetEpochSchedule(Method[Response[EpochSchedule]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the epoch schedule information from this cluster's genesis
        config

        #### Configuration Parameters Accepted:
        None"""
        if not configuration: 
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[EpochSchedule],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.EPOCH_SCHEDULE
            )
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
    
        return { **request, "params": self.add_configuration(parameters) }

