from typing import Any, Annotated
from pydantic import (
    Field,
    model_serializer,
)
from SolSystem.Models.Other.Other import PerformanceSample
from SolSystem.Models.Common import (
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)



type Samples = Annotated[int, Field(strict = True, gt = -1, le = 720)]



class GetRecentPerformanceSamples(Method[Response[list[PerformanceSample]]]):
    limit: Samples | None


    def __init__(
            self,
            limit: Samples | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns a list of recent performance samples, in reverse slot order.
        Performance samples are taken every 60 seconds and include the number
        of transactions and slots that occur in a given time window.
        
        ### Parameters
        `limit:` Number of samples to return (maximum 720)

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[list[PerformanceSample]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.RECENT_PERFORMANCE_SAMPLES
            ),
            configuration = configuration,
            limit = limit, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Samples | dict] = []
        if self.limit:
            parameters.append(self.limit)

        return { **request, "params": self.add_configuration(parameters) }
