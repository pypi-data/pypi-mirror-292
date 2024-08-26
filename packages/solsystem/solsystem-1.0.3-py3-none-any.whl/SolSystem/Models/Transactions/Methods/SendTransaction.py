from typing import Any
from pydantic import (
    field_validator,
    model_serializer,
)
from termcolor import colored
from SolSystem.Models.Transactions.Transaction import TransactionEncoding
from SolSystem.Models.Common import (
    Method,
    UInt64,
    Response,
    Base58Str,
    Base64Str,
    Signature,
    Commitment,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class SendTransaction(Method[Response[Signature]]):
    signed_transaction: Base64Str | Base58Str
    transaction_encoding: TransactionEncoding | None


    def __init__(
            self,
            signed_transaction: Base64Str | Base58Str,
            skip_preflight: bool | None = None,
            max_retries: UInt64 | None = None,
            transaction_encoding: TransactionEncoding | None = None,
            preflight_commitment: Commitment | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        If the node's rpc service receives the transaction, this method
        immediately succeeds, without waiting for any confirmations. A
        successful response from this method does not guarantee the transaction
        is processed or confirmed by the cluster.

        While the rpc service will reasonably retry to submit it, the
        transaction could be rejected if transaction's recent_blockhash
        expires before it lands. More details available
        in [documentation](https://solana.com/docs/rpc/http/sendtransaction)
        
        ### Parameters
        `signed_transaction:` Fully-signed Transaction, as encoded string.

        `skip_preflight:` When true, skip the preflight transaction checks

        `max_retries:` Maximum number of times for the RPC node to retry sending
        the transaction to the leader. If this parameter not provided, the RPC
        node will retry the transaction until it is finalized or until the
        blockhash expires.

        `min_context_slot:` Set the minimum slot at which to perform preflight
        transaction checks
        
        `transaction_encoding:` Encoding used for the transaction data.
        Base58 DEPRECATED

        `preflight_commitment:` Commitment level to use for preflight.

        #### Configuration Parameters Accepted:
        `min_context_slot`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("skip_preflight", skip_preflight)
        configuration.add_extra_field("max_retries", max_retries)
        configuration.add_extra_field("encoding", transaction_encoding)
        configuration.add_extra_field(
            "preflight_commitment",
            preflight_commitment,
        )
        configuration.filter_for_accepted_parameters([
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[Signature],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.SEND_TRANSACTION
            ),
            configuration = configuration,
            signed_transaction = signed_transaction, #type:ignore
        )



    @field_validator("transaction_encoding", mode = "after")
    @classmethod
    def validate_encoding(cls, v: TransactionEncoding) -> TransactionEncoding:
        if v not in (TransactionEncoding.BASE58, TransactionEncoding.BASE64):
            raise ValueError(
                colored(
                    "Only base58 and base64 encoding is supported for this operation.",
                    "light_red"
                )
            )
        return v


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Base58Str | Base64Str | dict] = [self.signed_transaction]

        return { **request, "params": self.add_configuration(parameters) }

            
