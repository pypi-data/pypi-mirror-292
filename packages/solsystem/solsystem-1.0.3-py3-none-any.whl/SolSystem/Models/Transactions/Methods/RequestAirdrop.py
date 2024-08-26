from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    Method,
    Lamports,
    Response,
    PublicKey,
    Base58Str,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class RequestAirdrop(Method[Response[Base58Str]]):
    target_account: PublicKey
    airdrop_amount: Lamports


    def __init__(
            self,
            target_account: PublicKey,
            airdrop_amount: Lamports,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Requests an airdrop of lamports to a Pubkey
    
        ### Parameters
        `target_account:` Pubkey of account to receive lamports

        `airdrop_amount:` Lamports to airdrop,

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = Response[Base58Str],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.REQUEST_AIRDROP
            ),
            configuration = configuration,
            target_account = target_account, #type:ignore
            airdrop_amount = airdrop_amount, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters = [self.target_account, self.airdrop_amount]

        return { **request, "params": self.add_configuration(parameters) }

            
