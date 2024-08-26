from typing import Any, Self, Annotated
from termcolor import colored
from pydantic import (
    Field,
    model_validator,
    model_serializer,
)
from SolSystem.Models.Accounts.Filters import Filter
from SolSystem.Models.Accounts.Account import ProgramAccount
from SolSystem.Models.Common import (
    Method,
    Encoding,
    Response,
    PublicKey,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



type Filters = Annotated[list[Filter], Field(max_length = 4)]
"""### Summary
As per solana documentation, requests are limited to 4 filters and request
must match to ALL filters requested.
---"""



class GetProgramAccounts(Method[Response[list[ProgramAccount]]]):
    program: PublicKey
    filters: Filters | None

    def __init__(
            self,
            program: PublicKey,
            filters: Filters | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the account information for a list of Pubkeys.
        
        ### Parameters
        `program:` Public key of program

        `filters:` Filter results using up to 4 filter objects

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`, `min_context_slot`, `data_slice`,
        `with_context`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("filters", filters)
        configuration.filter_for_accepted_parameters([
            ConfigurationField.ENCODING,
            ConfigurationField.COMMITMENT,
            ConfigurationField.DATA_SLICE,
            ConfigurationField.WITH_CONTEXT,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[list[ProgramAccount]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.PROGRAM_ACCOUNTS
            ),
            configuration = configuration,
            program = program, #type:ignore
            filters = filters, #type:ignore
        )


    @model_validator(mode = "after")
    def check_data_slice_validity(self) -> Self:
        assert self.configuration, colored("Configuration cannot be None","red")

        if self.configuration.encoding not in (
            Encoding.BASE58, Encoding.BASE64, Encoding.BASE64ZSTD
        ) and self.configuration.data_slice is not None:
            raise ValueError(
                colored(
                    (
                        "`data_slice` can only be used when the encoding is one of"
                        " base58, base64, or base64+zstd"
                    ),
                    "light_red"
                )
            )
        return self


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.program]
        
        return { **request, "params": self.add_configuration(parameters) }
