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



class GetTokenSupply(Method[Response[TokenAmount]]):
    mint: PublicKey

    def __init__(
            self,
            mint: PublicKey,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the total supply of an SPL Token type.
    
        ### Parameters:
        `mint:` Pubkey of Token account to query
        
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
                method = RPCMethodName.TOKEN_SUPPLY
            ),
            configuration = configuration,
            mint = mint, #type:ignore
        )



    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[PublicKey | dict] = [self.mint]
        
        return { **request, "params": self.add_configuration(parameters) }
