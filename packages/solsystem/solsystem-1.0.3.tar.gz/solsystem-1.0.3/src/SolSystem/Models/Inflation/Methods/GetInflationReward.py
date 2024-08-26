from typing import Any, Self
from termcolor import colored
from pydantic import model_serializer, model_validator
from SolSystem.Models.Inflation.Inflation import InflationReward
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    Base58Str,
    Commitment,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetInflationReward(Method[Response[list[InflationReward | None]]]):
    addresses: list[Base58Str]


    def __init__(
            self,
            addresses: list[Base58Str],
            epoch: UInt64 | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the inflation / staking reward for a list of addresses for
        an epoch
        
        ### Parameters
        `addresses:` List of addresses to query
        
        `epoch:` An epoch for which the reward occurs. If omitted, the previous
        epoch will be used

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
            response_type = Response[list[InflationReward | None]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.INFLATION_REWARD
            ),
            configuration = configuration,
            addresses = addresses, #type:ignore
        )



    @model_validator(mode = "after")
    def check_data_slice_validity(self) -> Self:
        assert self.configuration, colored("self.configuration cannot be None", "red")
        if self.configuration.commitment is Commitment.PROCESSED:
            raise ValueError(
                colored(
                    "`processed` is not supported for this operation",
                    "light_red"
                )
            )
        return self



    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[list[Base58Str] | dict] = []
        if self.addresses:
            parameters.append(self.addresses)
        
        return { **request, "params": self.add_configuration(parameters) }
