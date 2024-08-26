from typing import Any, Annotated
from pydantic import (
    Field,
    model_serializer,
)
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    PublicKey,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)



type SlotLimit = Annotated[int, Field(gt = 0, lt = 5000)]



class GetSlotLeaders(Method[Response[list[PublicKey]]]):
    start_slot: UInt64
    limit: SlotLimit


    def __init__(
            self,
            start_slot: UInt64,
            limit: SlotLimit,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the slot leaders for a given slot range

        ### Parameters
        `start_slot:` Start slot

        `limit:` limit between 1 and 5,000
        
        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[list[PublicKey]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.SLOT_LEADERS
            ),
            configuration = configuration,
            start_slot = start_slot, #type:ignore
            limit = limit, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[UInt64 | SlotLimit | dict] = []
        if self.start_slot:
            parameters.append(self.start_slot)
        if self.limit:
            parameters.append(self.limit)
        
        return { **request, "params": self.add_configuration(parameters) }

