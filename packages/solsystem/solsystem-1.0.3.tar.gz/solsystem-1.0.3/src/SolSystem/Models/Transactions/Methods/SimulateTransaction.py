from typing import Any, Self
from pydantic import (
    field_validator,
    model_validator,
    model_serializer,
)
from termcolor import colored
from SolSystem.Models.Accounts import ReturnAccounts
from SolSystem.Models.Transactions.Transaction import TransactionEncoding
from SolSystem.Models.Common import (
    Method,
    Response,
    Base64Str,
    Base58Str,
    Signature,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class SimulateTransaction(Method[Response[Signature]]):
    encoded_transaction: Base64Str | Base58Str
    transaction_encoding: TransactionEncoding | None
    

    def __init__(
            self,
            encoded_transaction: Base64Str | Base58Str,
            signature_verify: bool | None = None,
            replace_recent_blockhash: bool | None = None,
            include_inner_instructions: bool | None = None,
            accounts_configuration: ReturnAccounts | None = None,
            transaction_encoding: TransactionEncoding | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Simulate sending a transaction

        ### Parameters
        `encoded_transaction:` Transaction, as an encoded string. The
        transaction must have a valid blockhash, but is not required to be
        signed.

        `signature_verify:` If true the transaction signatures will be verified
        (conflicts with replaceRecentBlockhash)

        `replace_recent_blockhash:` If true the transaction recent blockhash
        will be replaced with the most recent blockhash. (conflicts with
        signature_verify)

        `include_inner_instructions:` If true the response will include inner
        instructions. These inner instructions will be jsonParsed where possible,
        otherwise json.
        
        `accounts_configuration:` Accounts configuration object
        #### Configuration Parameters Accepted:
        `min_context_slot`, `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("sig_verify", signature_verify)
        configuration.add_extra_field(
            "replace_recent_blockhash",
            replace_recent_blockhash,
        )
        configuration.add_extra_field("encoding", transaction_encoding)
        configuration.add_extra_field(
            "inner_instructions",
            include_inner_instructions,
        )
        configuration.add_extra_field(
            "accounts_configuration",
            accounts_configuration,
        )
        configuration.filter_for_accepted_parameters([
            ConfigurationField.MIN_CONTEXT_SLOT,
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = Response[Response[Signature]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.SIMULATE_TRANSACTION
            ),
            configuration = configuration,
            encoded_transaction = encoded_transaction, #type:ignore
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
    

    @model_validator(mode = "after")
    def validate_exclusive_options(self) -> Self:
        assert self.configuration, colored("self.configuration cannot be none", "red")
        if (
            self.configuration.sig_verify is not None
            and self.configuration.replace_recent_blockhash is not None
        ):
            raise ValueError(
                colored(
                    (
                        "Arguments `signature_verify` and `replace_recent_blockhash`"
                        " are mutually exclusive"
                    ),
                    "light_red"
                )
            )
        return self


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Base58Str | Base64Str | dict] = [self.encoded_transaction]
        
        return { **request, "params": self.add_configuration(parameters) }
