from typing import Any, Annotated
from pydantic import (
    Field,
    model_serializer,
)
from SolSystem.Models.Transactions.Transaction import SignatureStatus
from SolSystem.Models.Common import (
    Method,
    Response,
    Base58Str,
    RPCMethodName,
    Configuration,
    MethodMetadata,
)



type Signatures = Annotated[list[Base58Str], Field(max_length = 256)]



class GetSignatureStatus(Method[Response[list[SignatureStatus | None]]]):
    transaction_signatures: Signatures

    def __init__(
            self,
            transaction_signatures: Signatures,
            search_transaction_history: bool | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the statuses of a list of signatures. Each signature must be a 
        [txid](https://solana.com/docs/terminology#transaction-id),
        the first signature of a transaction.
    
        ### Parameters
        `transaction_signatures:` An array of transaction signatures to confirm
        up to a maximum of 256
    
        `search_transaction_history:` if true - a Solana node will search its ledger
        cache for any signatures not found in the recent status cache

        #### Configuration Parameters Accepted:"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field(
            "search_transaction_history",
            search_transaction_history,
        )
        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[list[SignatureStatus | None]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.SIGNATURE_STATUSES
            ),
            configuration = configuration,
            transaction_signatures = transaction_signatures, #type:ignore
        )



    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Signatures | dict] = [self.transaction_signatures]
        
        return { **request, "params": self.add_configuration(parameters) }
