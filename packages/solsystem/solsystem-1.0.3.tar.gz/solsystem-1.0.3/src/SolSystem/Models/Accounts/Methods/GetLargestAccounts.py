from typing import Any
from enum import StrEnum
from pydantic import (
    BaseModel,
    model_serializer,
)
from SolSystem.Models.Common import (
    PublicKey,
    Lamports,
    Response,
    Method,
    MethodMetadata,
    RPCMethodName,
    Configuration,
    ConfigurationField,
)


class AccountFilter(StrEnum):
    CIRCULATING = "circulating"
    NON_CIRCULATING = "nonCirculating"



class LargestAccount(BaseModel):
    address: PublicKey
    lamports: Lamports



class GetLargestAccounts(Method[Response[list[LargestAccount]]]):
    account_filter: AccountFilter | None = None

    def __init__(
            self,
            account_filter: AccountFilter | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the 20 largest accounts, by lamport balance (results may be
        cached up to two hours)

        NOTE: This method is unavailable on Solana mainnet or Helius. Others
        not tested
        
        ### Parameters
        `account_filter:` Filter results by account type

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("filter", account_filter)
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])

        super().__init__(
            response_type = Response[list[LargestAccount]],
            metadata = (
                MethodMetadata[RPCMethodName](method = RPCMethodName.LARGEST_ACCOUNTS)
            ),
            configuration = configuration,
            account_filter = account_filter, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = []
    
        return { **request, "params": self.add_configuration(parameters) }
