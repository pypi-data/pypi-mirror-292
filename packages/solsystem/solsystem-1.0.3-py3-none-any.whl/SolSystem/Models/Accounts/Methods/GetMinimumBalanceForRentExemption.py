from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Lamports,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)


class GetMinimumBalanceForAccountRentExemption(Method[Response[Lamports]]):
    data_size: UInt64


    def __init__(
            self,
            data_size: UInt64,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns minimum balance required to make account rent exempt.
        
        ### Parameters
        `data_size:` The accounts data size

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
                method = RPCMethodName.MINIMUM_BALANCE_FOR_RENT_EXEMPTION
            ),
            configuration = configuration,
            data_size = data_size, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        if self.data_size:
            parameters.append(self.data_size)
        
        return { **request, "params": self.add_configuration(parameters) }
