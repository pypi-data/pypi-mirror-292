from __future__ import annotations
from typing import Any
from enum import StrEnum
from pydantic.alias_generators import to_camel
from pydantic import BaseModel, ConfigDict, model_serializer
from SolSystem.Models.Common import (
    UInt64,
    Int64,
    WsMethod,
    WsResponse,
    WsMethodName,
    Configuration,
    MethodMetadata,
)



class SlotUpdateStats(BaseModel):
    """### Summary
    Error message. Only present if the update type of slotUpdates is "frozen".
    
    ### Parameters

    ```python
    max_transactions_per_entry  : UInt64
    num_failed_transactions     : UInt64
    num_successful_transactions : UInt64
    num_transaction_entries     : UInt64
    ```"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True
    )

    max_transactions_per_entry: UInt64
    num_failed_transactions: UInt64
    num_successful_transactions: UInt64
    num_transaction_entries: UInt64



class SlotUpdatesType(StrEnum):
    FIRST_SHRED_RECEIVED    = "firstShredReceived"
    COMPLETED               = "completed"
    CREATED_BANK            = "createdBank"
    FROZEN                  = "frozen"
    DEAD                    = "dead"
    OPTIMISTIC_CONFIRMATION = "optimisticConfirmation"
    ROOT                    = "root"



class SlotUpdatesNotification(BaseModel):
    """### Summary
    Information provided by the slot subscription.
    
    ### Parameters
    ```python
    err       : str | None = None
    parent    : UInt64 | None = None
    slot      : UInt64
    stats     : SlotUpdateStats | None = None
    timestamp : Int64
    type      : SlotUpdatesType
    ```"""
    err: str | None = None
    parent: UInt64 | None = None
    slot: UInt64
    stats: SlotUpdateStats | None = None
    timestamp: Int64
    type: SlotUpdatesType



class WsGetSlotUpdates(WsMethod[WsResponse[SlotUpdatesNotification]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Subscribe to receive a notification from the validator on a variety of
        updates on every slot.

        NOTE: This method is considered unstable and may change in the future. 
        It may not always be supported by the RPC provider.

        #### Configuration Parameters Accepted: 
        None"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = WsResponse[SlotUpdatesNotification],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.SLOTS_UPDATES),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = []
        return { **request, "params": self.add_configuration(parameters) }
