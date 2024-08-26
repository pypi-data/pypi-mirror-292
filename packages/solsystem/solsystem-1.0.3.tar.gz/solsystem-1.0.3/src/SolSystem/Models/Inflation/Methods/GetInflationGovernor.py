from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Inflation.Inflation import InflationGovernor
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetInflationGovernor(Method[Response[InflationGovernor]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the current inflation governor

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = Response[InflationGovernor],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.INFLATION_GOVERNOR
            ),
            configuration = configuration
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
        
        return { **request, "params": self.add_configuration(parameters) }
