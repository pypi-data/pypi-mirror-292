from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Other.Other import Supply
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetSupply(Method[Response[Supply]]):
    def __init__(
            self,
            exclude_non_circulating_accounts_list: bool | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns information about the current supply.
        
        ### Parameters
        `exclude_non_circulating_accounts_list:` exclude non circulating
        accounts list from response

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field(
            "exclude_non_circulating_accounts_list",
            exclude_non_circulating_accounts_list,
        )
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = Response[Supply],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.SUPPLY
            ),
            configuration = configuration,
        )


    @model_serializer()
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        return { **request, "params": self.add_configuration(parameters) }
            
