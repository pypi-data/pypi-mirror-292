from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Blocks.Blocks import Block
from SolSystem.Models.Transactions.Transaction import TransactionDetail
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetBlock(Method[Response[Block]]):
    slot_number: UInt64

    def __init__(
            self,
            slot_number: UInt64,
            transaction_details: TransactionDetail = TransactionDetail.FULL,
            rewards: bool | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns identity and transaction information about a confirmed block
        in the ledger
        
        ### Parameters
        `slot_number:` Slot number

        `transaction_details:` Level of transaction detail to return

        `rewards:` whether to populate the rewards array. If parameter not
        provided, the default includes rewards.

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`, `max_supported_transaction_version`"""
        if not configuration:
            configuration = Configuration()
        
        configuration.add_extra_field("transaction_details", transaction_details)
        configuration.add_extra_field("rewards", rewards)
        configuration.filter_for_accepted_parameters([
            ConfigurationField.ENCODING,
            ConfigurationField.COMMITMENT,
            ConfigurationField.MAX_SUPPORTED_TRANSACTION_VERSION,
            
        ])
        super().__init__(
            response_type = Response[Block],
            metadata = MethodMetadata[RPCMethodName](method = RPCMethodName.BLOCK),
            configuration = configuration,
            slot_number = slot_number, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[UInt64 | dict] = [self.slot_number]
        
        return { **request, "params": self.add_configuration(parameters) }