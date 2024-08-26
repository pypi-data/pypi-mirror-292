from __future__ import annotations
from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    WsMethod,
    WsResponse,
    WsMethodName,
    Configuration,
    MethodMetadata,
)



class WsGetRoot(WsMethod[WsResponse[int]]):
    def __init__(
            self,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Recieve a notification when the validator sets a new root."""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = WsResponse[int],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.ROOT),
            configuration = configuration
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        return self.metadata.model_dump()
