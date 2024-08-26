from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    Method,
    Response,
    PublicKey,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetSlotLeader(Method[Response[PublicKey]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the current slot leader

        #### Configuration Parameters Accepted:
        `min_context_slot`, `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[PublicKey],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.SLOT_LEADER
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        return { **request, "params": self.add_configuration(parameters) }

