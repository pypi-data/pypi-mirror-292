from typing import Any, Annotated
from pydantic import (
    Field,
    model_serializer,
)
from SolSystem.Models.Blocks.Blocks import PrioritizationFee
from SolSystem.Models.Common import (
    Method,
    Response,
    PublicKey,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)



type Addresses = Annotated[list[PublicKey], Field(max_length = 128)]



class GetRecentPrioritizationFees(Method[Response[list[PrioritizationFee]]]):
    accounts: Addresses | None = None


    def __init__(
            self,
            accounts: Addresses | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns a list of prioritization fees from recent blocks. Currently,
        a node's prioritization-fee cache stores data from up to 150 blocks.
        
        ### Parameters
        `accounts:` If this parameter is provided, the response will reflect
        a fee to land a transaction locking all of the provided accounts as
        writable. Max of 128 Addresses allowed.

        #### Configuration Parameters Accepted:
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[list[PrioritizationFee]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.RECENT_PRIORITIZATION_FEES
            ),
            configuration = configuration,
            accounts = accounts, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Addresses | dict] = []
        if self.accounts:
            parameters.append(self.accounts)
        
        return { **request, "params": self.add_configuration(parameters) }
