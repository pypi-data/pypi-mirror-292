from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Accounts.Account import Account
from SolSystem.Models.Common import (
    WsMethod,
    WsResponse,
    PublicKey,
    WsMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class WsGetAccountInfo(WsMethod[WsResponse[Account]]):
    account: PublicKey

    def __init__(
            self,
            account: PublicKey,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Object providing subscription and unsubscription methods for AccountInfo
        
        ### Parameters
        `account:` Pubkey of account to query

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.ENCODING,
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = WsResponse[Account],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.ACCOUNT),
            configuration = configuration,
            account = account, #type:ignore
        )



    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.account]
        return { **request, "params": self.add_configuration(parameters) }
