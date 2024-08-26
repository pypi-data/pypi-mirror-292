from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Slots.Slots import SnapshotSlot
from SolSystem.Models.Common import (
    Method,
    Response,
    MethodMetadata,
    RPCMethodName,
    Configuration,
)



class GetHighestSnapshotSlot(Method[Response[SnapshotSlot]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the highest slot information that the node has snapshots for.
        This will find the highest full snapshot slot, and the highest 
        incremental snapshot slot based on the full snapshot slot, if there
        is one.

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[SnapshotSlot],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.HIGHEST_SNAPSHOT_SLOT
            ),
            configuration = configuration,
        )


    @model_serializer()
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []

        return { **request, "params": self.add_configuration(parameters) }

