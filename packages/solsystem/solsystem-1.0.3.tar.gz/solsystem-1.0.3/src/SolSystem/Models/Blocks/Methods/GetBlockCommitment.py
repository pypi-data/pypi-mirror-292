from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Blocks.Blocks import BlockCommitment
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)


class GetBlockCommitment(Method[Response[BlockCommitment]]):
    block_number: UInt64

    def __init__(
            self,
            block_number: UInt64,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns commitment for particular block
        
        ### Parameters
        `block_number:` block number, identified by Slot

        #### Configuration Parameters Accepted:"""
        if not configuration:
            configuration = Configuration()
        
        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[BlockCommitment],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.BLOCK_COMMITMENT
            ),
            configuration = configuration,
            block_number = block_number, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[UInt64 | dict] = [self.block_number]
        
        return { **request, "params": self.add_configuration(parameters) }
