from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    Method,
    Response,
    Base58Str,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class IsBlockhashValid(Method[Response[bool]]):
    blockhash: Base58Str


    def __init__(
            self,
            blockhash: Base58Str,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns whether a blockhash is still valid or not.
        
        ### Parameters
        `blockhash:` The blockhash of the block to evaluate

        #### Configuration Parameters Accepted:
        `commitment`, `min_context_slot`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[bool],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.IS_BLOCKHASH_VALID
            ),
            configuration = configuration,
            blockhash = blockhash, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Base58Str | dict] = [self.blockhash]
        
        return { **request, "params": self.add_configuration(parameters) }

            
