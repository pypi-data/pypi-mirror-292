from typing import Any, Self
from termcolor import colored
from pydantic import (
    model_validator,
    field_validator,
    model_serializer,
)
from SolSystem.Models.Accounts.Account import Account
from SolSystem.Models.Common import (
    PublicKey,
    Encoding,
    Response,
    Method,
    MethodMetadata,
    RPCMethodName,
    Configuration,
    ConfigurationField,
)



class GetMultipleAccounts(Method[Response[list[Account]]]):
    accounts: list[PublicKey]


    def __init__(
            self,
            accounts: list[PublicKey],
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the account information for a list of Pubkeys.
        
        ### Parameters
        `accounts:` List of no more than 100 accounts to query

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`, `min_context_slot`, `data_slice`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.ENCODING,
            ConfigurationField.COMMITMENT,
            ConfigurationField.DATA_SLICE,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[list[Account]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.MULTIPLE_ACCOUNTS
            ),
            configuration = configuration,
            accounts = accounts, #type:ignore
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
                        "`data_slice` can only be used when the encoding is one"
                        " of base58, base64, or base64+zstd"
                    ),
                    "light_red"
                )
            )
        return self
    

    @field_validator("accounts", mode = "after")
    @classmethod
    def check_account_list_length(cls, v: list[PublicKey]) -> list[PublicKey]:
        if len(v) > 100:
            raise ValueError(
                colored(
                    (
                        "`accounts` must specify no more than 100 entries for"
                        " the query"
                    ),
                    "light_red"
                )
            )
        return v


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.accounts]
        
        return { **request, "params": self.add_configuration(parameters) }
