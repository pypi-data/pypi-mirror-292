from __future__ import annotations
from pydantic import (
    BaseModel,
    ConfigDict,
    model_serializer,
)
from typing import Any, Literal
from pydantic.alias_generators import to_camel
from SolSystem.Models.Blocks.Blocks import Block
from SolSystem.Models.Transactions.Transaction import TransactionDetail
from SolSystem.Models.Common import (
    UInt64,
    WsMethod,
    WsResponse,
    PublicKey,
    WsMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class BlockAccountFilter(BaseModel):
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True
    )
    mentions_account_or_program: PublicKey



class BlockNotification(BaseModel):
    """### Summary
    The broadcasted block information is slightly different from the typical
    response from `GetBlock` because it includes the slot number of this block
    and an optional error message.
    
    For more details on the actual `Block` type please refer to
    SolSystem.Models.Blocks.Block"""
    slot: UInt64
    err: dict | None = None
    block: Block | None = None



class WsGetBlock(WsMethod[WsResponse[BlockNotification]]):
    filter: Literal["all"] | BlockAccountFilter
    show_rewards: bool | None
    transaction_details: TransactionDetail

    def __init__(
            self,
            filter: Literal["all"] | BlockAccountFilter = "all",
            show_rewards: bool | None = None,
            transaction_details: TransactionDetail = TransactionDetail.FULL,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Recieve a notification any time a new block is confirmed or finalized.
        
        NOTE This subscription is considered unstable and is only available if the
        validator was started with the --rpc-pubsub-enable-block-subscription
        flag. The format of this subscription may change in the future. Please
        refer to the [documentation](https://solana.com/docs/rpc/websocket/blocksubscribe)
        
        ### Parameters
        `filter:` Either include all transactions in the block or only include
        transactions mentioning the specific public key

        `show_rewards:` Whether to populate the rewards array. If parameter
        not provided, the default includes rewards.

        `transaction_details:` Level of transaction detail to return

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`, `max_supported_transaction_version`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.ENCODING,
            ConfigurationField.COMMITMENT,
            ConfigurationField.MAX_SUPPORTED_TRANSACTION_VERSION,
        ])
        super().__init__(
            response_type = WsResponse[BlockNotification],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.BLOCK),
            configuration = configuration,
            filter = filter, # type:ignore
            show_rewards = show_rewards, # type:ignore
            transaction_details = transaction_details, # type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.filter]
        return { **request, "params": self.add_configuration(parameters) }
