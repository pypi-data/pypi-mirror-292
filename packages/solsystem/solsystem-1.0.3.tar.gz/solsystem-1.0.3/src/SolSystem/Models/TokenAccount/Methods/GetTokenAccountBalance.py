from typing import Any
from pydantic import model_serializer
from SolSystem.Models.TokenAccount.TokenAccount import TokenAmount
from SolSystem.Models.Common import (
    Method,
    Response,
    PublicKey,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetTokenAccountBalance(Method[Response[TokenAmount]]):
    token_account: PublicKey


    def __init__(
            self,
            token_account: PublicKey,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the token balance of an SPL Token account.
    
        ### Parameters:
        `token_account:` Pubkey of Token account to query
        
        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = Response[TokenAmount],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.TOKEN_ACCOUNT_BALANCE
            ),
            configuration = configuration,
            token_account = token_account, #type:ignore
        )



    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[PublicKey | dict] = [self.token_account]
        
        return { **request, "params": self.add_configuration(parameters) }
