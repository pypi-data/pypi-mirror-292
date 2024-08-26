from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Blocks.Blocks import (
    BlockProduction,
    SlotRange,
)
from SolSystem.Models.Common import (
    Method,
    Response,
    Base58Str,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetBlockProduction(Method[Response[BlockProduction]]):
    def __init__(
            self,
            identity: Base58Str | None = None,
            slot_range: SlotRange | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the account information for a list of Pubkeys.
        
        ### Parameters
        `identity:` Only return results for this validator identity

        `slot_range:` Slot range to return block production for. If parameter
        not provided, defaults to current epoch.

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()
        
        configuration.add_extra_field("identity", identity)
        configuration.add_extra_field("slot_range", slot_range)
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = Response[BlockProduction],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.BLOCK_PRODUCTION
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        
        return { **request, "params": self.add_configuration(parameters) }

