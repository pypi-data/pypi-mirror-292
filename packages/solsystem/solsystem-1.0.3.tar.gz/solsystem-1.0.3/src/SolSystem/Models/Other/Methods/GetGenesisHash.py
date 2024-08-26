from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    Base58Str,
    Response,
    Method,
    MethodMetadata,
    RPCMethodName,
    Configuration,
)


class GetGenesisHash(Method[Response[Base58Str]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the genesis hash

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[Base58Str],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.GENESIS_HASH
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []

        return { **request, "params": self.add_configuration(parameters) }
