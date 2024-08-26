from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Inflation.Inflation import InflationRate
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)


class GetInflationRate(Method[Response[InflationRate]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Inflation values for current epoch

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[InflationRate],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.INFLATION_RATE
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
    
        return { **request, "params": self.add_configuration(parameters) }
