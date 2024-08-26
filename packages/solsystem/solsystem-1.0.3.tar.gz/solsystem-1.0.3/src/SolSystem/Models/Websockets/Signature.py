from __future__ import annotations
from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Common import (
    WsMethod,
    Base58Str,
    WsResponse,
    WsMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)


class WsGetSignature(WsMethod[WsResponse[dict | str | None]]):
    transaction_signature: Base58Str

    def __init__(
            self,
            transaction_signature: Base58Str,
            enable_recieved_notification: bool = False,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Subscribe to receive a notification when the transaction with the given
        signature reaches the specified commitment level.

        NOTE that this is a subscription to a single notificaion and after it is
        recieved, the subscription will be automatically closed by the server.
        
        ### Parameters
        `transaction_signature:` The transaction signature must be the first
        signature from the transaction as a base58 encoded string.

        `enable_recieved_notification:` Whether or not to subscribe for
        notifications when signatures are received by the RPC, in addition to
        when they are processed.

        #### Configuration Parameters Accepted:
        `encoding`, `enableReceivedNotification`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field(
            name = "enableReceivedNotification",
            value = enable_recieved_notification,
        )

        configuration.filter_for_accepted_parameters([
            ConfigurationField.ENCODING,
            ConfigurationField.COMMITMENT,
            ConfigurationField.MAX_SUPPORTED_TRANSACTION_VERSION,
        ])
        super().__init__(
            response_type = WsResponse[dict | str | None],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.SIGNATURE),
            configuration = configuration,
            transaction_signature = transaction_signature, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.transaction_signature]
        return { **request, "params": self.add_configuration(parameters) }
