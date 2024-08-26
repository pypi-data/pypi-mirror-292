from typing import Any, Self
from termcolor import colored
from pydantic import (
    model_validator,
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



class GetAccountInfo(Method[Response[Account]]):
    account: PublicKey 

    def __init__(
            self,
            account: PublicKey,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns all information associated with the account of provided Pubkey
        
        ### Parameters
        `account:` Public key of account to query

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`, `min_context_slot`, `data_slice`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.ENCODING,
            ConfigurationField.COMMITMENT,
            ConfigurationField.MIN_CONTEXT_SLOT,
            ConfigurationField.DATA_SLICE,
        ])
        super().__init__(
            response_type = Response[Account],
            metadata = (
                MethodMetadata[RPCMethodName](method = RPCMethodName.ACCOUNT_INFO)
            ),
            configuration = configuration,
            account = account, #type:ignore
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



    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.account]

        return { **request, "params": self.add_configuration(parameters) }
