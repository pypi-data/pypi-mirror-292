from typing import Any, Self
from termcolor import colored
from pydantic import (
    model_serializer,
    model_validator,
)
from SolSystem.Models.Transactions.Transaction import (
    Transaction,
    TransactionEncoding,
)
from SolSystem.Models.Common import (
    Method,
    Response,
    Base58Str,
    RPCMethodName,
    Commitment,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class GetTransaction(Method[Response[Transaction | None]]):
    transaction_signature: Base58Str


    def __init__(
            self,
            transaction_signature: Base58Str,
            transaction_encoding: TransactionEncoding = TransactionEncoding.JSON,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns transaction details for a confirmed transaction
    
        ### Parameters
        `transaction_signature:` Transaction signature to search.

        `transaction_encoding`: Return transaction data encoded in this format.

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`, `max_supported_transaction_version`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("encoding", transaction_encoding)
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MAX_SUPPORTED_TRANSACTION_VERSION,
        ])
        super().__init__(
            response_type = Response[Transaction | None],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.TRANSACTION
            ),
            configuration = configuration,
            transaction_signature = transaction_signature, #type:ignore
        )



    @model_validator(mode = "after")
    def check_data_slice_validity(self) -> Self:
        assert self.configuration, colored("self.configuration cannot be None", "red")
        if self.configuration.commitment is Commitment.PROCESSED:
            raise ValueError(
                colored(
                    "`processed` is not supported for this operation",
                    "light_red"
                )
            )
        return self


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Base58Str | dict] = [self.transaction_signature]
        return { **request, "params": self.add_configuration(parameters) }
