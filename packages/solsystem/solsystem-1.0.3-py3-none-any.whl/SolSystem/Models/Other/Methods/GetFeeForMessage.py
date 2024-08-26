from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    Base64Str,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetFeeForMessage(Method[Response[UInt64 | None]]):
    message: Base64Str

    def __init__(
            self,
            message: Base64Str,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Get the fee the network will charge for a particular Message
        
        NOTE: Only available on solana core v1.9 or newer

        ### Parameters
        `message:` Encoded Message

        #### Configuration Parameters Accepted:
        `commitment`, `min_context_slot`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[UInt64 | None],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.FEE_FOR_MESSAGE
            ),
            configuration = configuration,
            message = message, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Base64Str | dict] = [self.message]

        return { **request, "params": self.add_configuration(parameters) }
