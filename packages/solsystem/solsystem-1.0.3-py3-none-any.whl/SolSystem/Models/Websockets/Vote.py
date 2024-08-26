from __future__ import annotations
from typing import Any
from pydantic.alias_generators import to_camel
from pydantic import BaseModel, ConfigDict, model_serializer
from SolSystem.Models.Common import (
    UInt64,
    Int64,
    WsMethod,
    Base58Str,
    PublicKey,
    WsResponse,
    WsMethodName,
    Configuration,
    MethodMetadata,
)


class VoteNotification(BaseModel):
    """### Summary
    Information provided by the vote subscription.
    
    ### Parameters
    ```python
    hash        : str
    slots       : list[UInt64]
    timestamp   : Int64 | None = None
    signature   : Base58Str | None = None
    vote_pubkey : PublicKey | None = None
    ```"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True
    )

    hash: str
    slots: list[UInt64]
    timestamp: Int64 | None = None
    signature: Base58Str | None = None
    vote_pubkey: PublicKey | None = None



class WsGetVote(WsMethod[WsResponse[VoteNotification]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Subscribe to receive notification anytime a new vote is observed in
        gossip. These votes are pre-consensus therefore there is no guarantee
        these votes will enter the ledger.

        NOTE: This subscription is unstable and only available if the validator
        was started with the --rpc-pubsub-enable-vote-subscription flag. The
        format of this subscription may change in the future.

        #### Configuration Parameters Accepted: 
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = WsResponse[VoteNotification],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.VOTE),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = []
        return { **request, "params": self.add_configuration(parameters) }
