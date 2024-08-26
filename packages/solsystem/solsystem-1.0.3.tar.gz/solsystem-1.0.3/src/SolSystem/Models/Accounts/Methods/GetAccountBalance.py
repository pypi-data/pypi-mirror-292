from typing import Any
from termcolor import colored
from pydantic import model_serializer
from SolSystem.Models.Common import (
    Method,
    Response,
    Lamports,
    PublicKey,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetAccountBalance(Method[Response[Lamports]]):
    account: PublicKey    

    def __init__(
            self,
            account: PublicKey,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the lamport balance of the account of provided Pubkey
        
        ### Parameters
        `account:` Public key of account to query

        #### Configuration Parameters Accepted:
        `commitment`, `min_context_slot`"""
        if not configuration:
            configuration = Configuration()
        
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])

        super().__init__(
            response_type = Response[Lamports],
            metadata = (
                MethodMetadata[RPCMethodName](method = RPCMethodName.BALANCE)
            ),
            account = account, #type:ignore
            configuration = configuration, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.account]

        return { **request, "params": self.add_configuration(parameters) }
