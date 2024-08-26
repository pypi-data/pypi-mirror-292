from typing import Any, Self
from termcolor import colored
from pydantic import (
    model_validator,
    model_serializer,
)
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    Commitment,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)


class GetBlocksWithLimit(Method[Response[list[UInt64]]]):
    start_slot: UInt64
    limit: UInt64

    def __init__(
            self,
            start_slot: UInt64,
            limit: UInt64,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns a list of confirmed blocks starting at the given slot

        ### Parameters
        `start_slot:` start_slot
        
        `limit:` Must be no more than 500,000

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()
        if not configuration.commitment:
            configuration.commitment = Commitment.FINALIZED

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT
        ])

        super().__init__(
            response_type = Response[list[UInt64]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.BLOCKS_WITH_LIMIT
            ),
            configuration = configuration,
            start_slot = start_slot, #type:ignore
            limit = limit, #type:ignore
        )


    @model_validator(mode = "after")
    def validate_commitment(self) -> Self:
        if self.limit > 500_000:
            raise ValueError(
                "limit must be no more than 500,000"
            )
        
        assert self.configuration, colored("self.configuration cannot be null", "red")
        if self.configuration.commitment == Commitment.PROCESSED:
            raise ValueError("commitment of 'processed' is not supported.")
        return self


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[UInt64 | dict] = [self.start_slot, self.limit]
        
        return { **request, "params": self.add_configuration(parameters) }
