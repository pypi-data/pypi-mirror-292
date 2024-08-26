from typing import Any, Self
from pydantic import (
    model_validator,
    model_serializer,
)
from termcolor import colored
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


class GetBlocks(Method[Response[list[UInt64]]]):
    start_slot: UInt64
    end_slot: UInt64 | None

    def __init__(
            self,
            start_slot: UInt64,
            end_slot: UInt64 | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns  an array of u64 integers listing confirmed blocks between
        start_slot and either end_slot - if provided, or latest confirmed block,
        inclusive. Max range allowed is 500,000 slots.

        ### Parameters
        `start_slot:` start_slot
        
        `end_slot:` end_slot, must be no more than 500,000 blocks higher than
        the start_slot

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
                method = RPCMethodName.BLOCKS
            ),
            configuration = configuration,
            start_slot = start_slot, #type:ignore
            end_slot = end_slot, #type:ignore
        )


    @model_validator(mode = "after")
    def validate_end_slot(self) -> Self:
        assert self.configuration, colored("self.configuration cannot be None", "red")
        if self.end_slot:
            if self.end_slot - self.start_slot > 500_000:
                raise ValueError(
                    "end_slot must be no more than 500,000 greater than start_slot"
                )
        
        if self.configuration.commitment == Commitment.PROCESSED:
            raise ValueError("commitment of 'processed' is not supported.")
        return self


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[UInt64 | dict] = [self.start_slot]
        if self.end_slot:
            parameters.append(self.end_slot)
        
        return { **request, "params": self.add_configuration(parameters) }