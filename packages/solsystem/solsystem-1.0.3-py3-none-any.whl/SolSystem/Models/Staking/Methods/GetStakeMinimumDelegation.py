from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    Method,
    Lamports,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetStakeMinimumDelegation(Method[Response[Lamports]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the stake minimum delegation, in lamports.

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = Response[Lamports],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.STAKE_MINIMUM_DELEGATION
            ),
            configuration = configuration,
        )

    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        return { **request, "params": self.add_configuration(parameters) }
