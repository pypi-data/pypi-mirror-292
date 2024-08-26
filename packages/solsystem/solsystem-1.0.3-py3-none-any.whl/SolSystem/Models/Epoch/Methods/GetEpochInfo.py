from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Epoch.Epoch import EpochInfo
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetEpochInfo(Method[Response[EpochInfo]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns information about the current epoch

        #### Configuration Parameters Accepted:
        `commitment`, `min_context_slot`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[EpochInfo],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.EPOCH_INFO
            ),
            configuration = configuration
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []

        return { **request, "params": self.add_configuration(parameters) }
