from termcolor import colored
from typing import Any, Annotated
from pydantic import (
    Field,
    field_validator,
    model_serializer,
)
from SolSystem.Models.Transactions.Transaction import TransactionSignature
from SolSystem.Models.Common import (
    Method,
    Response,
    PublicKey,
    Commitment,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



type SignatureCount = Annotated[int, Field(gt = -1, lt = 1001)]



class GetSignaturesForAddress(Method[Response[list[TransactionSignature]]]):
    account: PublicKey


    def __init__(
            self,
            account: PublicKey,
            limit: SignatureCount | None = 1000,
            before: str | None = None,
            until: str | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns signatures for confirmed transactions that include the given
        address in their accountKeys list. Returns signatures from newest to
        oldest in time from the provided signature or most recent confirmed
        block. 
        
        ### Parameters
        `account:` Account address

        `limit:` Maximum transaction signatures to return (between 1 and 1,000
        
        `before:` Start searching backwards from this transaction signature.
        If not provided the search starts from the top of the highest max
        confirmed block.
        
        `until:` Search until this transaction signature, if found before limit
        reached

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`, `min_context_slot`, `data_slice`,
        `with_context`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("limit", limit)
        configuration.add_extra_field("before", before)
        configuration.add_extra_field("until", until)
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[list[TransactionSignature]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.SIGNATURES_FOR_ADDRESS
            ),
            configuration = configuration,
            account = account, #type:ignore
        )


    @field_validator("configuration", mode = "after")
    @classmethod
    def validate_encoding(cls, v: Configuration) -> Configuration:
        if v.commitment:
            if v.commitment not in (Commitment.CONFIRMED, Commitment.FINALIZED):
                raise ValueError(
                    colored(
                        "Does not support commitment level below CONFIRMED",
                        "red"
                    )
                )
        return v
    

    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[PublicKey | dict] = [self.account]
        
        return { **request, "params": self.add_configuration(parameters) }
