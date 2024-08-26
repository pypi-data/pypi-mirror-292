from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    Int64,
    UInt64,
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)


class GetBlockTime(Method[Response[Int64]]):
    block_number: UInt64

    def __init__(
            self,
            block_number: UInt64,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Each validator reports their UTC time to the ledger on a regular interval
        by intermittently adding a timestamp to a Vote for a particular block.
        A requested block's time is calculated from the stake-weighted mean of the
        Vote timestamps in a set of recent blocks recorded on the ledger. When a 
        block time is unavailable an error is returned.
        
        ### Parameters
        `block_number:` as identified by the slot.

        #### Configuration Parameters Accepted:"""
        if not configuration:
            configuration = Configuration()
        
        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[Int64],
            metadata =  MethodMetadata[RPCMethodName](
                method = RPCMethodName.BLOCK_TIME
            ),
            configuration = configuration,
            block_number = block_number, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Int64 | dict] = [self.block_number]
        
        return { **request, "params": self.add_configuration(parameters) }
