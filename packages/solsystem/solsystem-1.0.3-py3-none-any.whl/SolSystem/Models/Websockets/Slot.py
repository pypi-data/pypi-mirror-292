from __future__ import annotations
from typing import Any
from pydantic import BaseModel, model_serializer
from SolSystem.Models.Common import (
    UInt64,
    WsMethod,
    WsResponse,
    WsMethodName,
    Configuration,
    MethodMetadata,
)



class SlotNotification(BaseModel):
    """### Summary
    Information provided by the slot subscription.
    
    ### Parameters
    ```python
    parent: UInt64
    root: UInt64
    slot: UInt64
    ```"""
    parent: UInt64
    root: UInt64
    slot: UInt64



class WsGetSlot(WsMethod[WsResponse[SlotNotification]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Subscribe to receive notification anytime a slot is processed by the validator

        #### Configuration Parameters Accepted:
        `encoding`, `enableReceivedNotification`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = WsResponse[SlotNotification],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.SLOT),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = []
        return { **request, "params": self.add_configuration(parameters) }
