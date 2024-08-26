from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Staking.Staking import StakeActivation
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    PublicKey,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetStakeActivation(Method[Response[StakeActivation]]):
    account: PublicKey

    def __init__(
            self,
            account: PublicKey,
            epoch: UInt64 | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns epoch activation information for a stake account
    
        ### Parameters:
        `account:` Pubkey of stake Account to query
        
        `epoch:` DEPRECATED. Epoch for which to calculate activation details. If
        parameter not provided, defaults to current epoch. Inputs other than the
        current epoch return an error.

        #### Configuration Parameters Accepted:
        `commitment`, `min_context_slot`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("epoch", epoch)
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[StakeActivation],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.STAKE_ACTIVATION
            ),
            configuration = configuration,
            account = account, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[PublicKey | dict] = []
        if self.account:
            parameters.append(self.account)

        return { **request, "params": self.add_configuration(parameters) }
