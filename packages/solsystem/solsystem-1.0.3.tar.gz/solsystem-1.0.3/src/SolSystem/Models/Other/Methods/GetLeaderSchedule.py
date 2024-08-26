from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    Base58Str,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



type LeaderSchedule = dict[Base58Str, list[int]]
"""### Summary
Validator identities and their corresponding leader slot indices as values
(indices are relative to the first slot in the requested epoch)
---"""



class GetLeaderSchedule(Method[Response[LeaderSchedule | None]]):
    slot: UInt64 | None = None

    def __init__(
            self,
            slot: UInt64 | None = None,
            identity: Base58Str | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the leader schedule for an epoch
        
        ### Parameters
        `epoch:` Fetch the leader schedule for the epoch that corresponds to
        the provided slot. If unspecified, the leader schedule for the current
        epoch is fetched.

        `identity:` Only return results for this validator identity

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("identity", identity)
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = Response[LeaderSchedule | None],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.LEADER_SCHEDULE
            ),
            configuration = configuration,
            slot = slot, #type:ignore 
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[UInt64 | dict] = []
        if self.slot:
            parameters.append(self.slot)

        return { **request, "params": self.add_configuration(parameters) }
