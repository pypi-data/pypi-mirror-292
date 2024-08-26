from typing import Any, Self
from termcolor import colored
from pydantic import (
    model_serializer,
    model_validator,
)
from SolSystem.Models.TokenAccount.TokenAccount import TokenAccount
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



class GetTokenAccountsByDelegate(Method[Response[list[TokenAccount]]]):
    account_delegate: PublicKey
    mint: PublicKey | None = None
    program_id: PublicKey | None = None


    def __init__(
            self,
            account_delegate: PublicKey,
            mint: PublicKey | None = None,
            program_id: PublicKey | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the token balance of an SPL Token account. Note that the
        arguments `mint` and `program_id` are mutually exclusive. You MUST
        specify mint or program_id.
    
        ### Parameters:
        `account_delegate:` Pubkey of account delegate to query

        `mint:` Pubkey of the specific token Mint to limit accounts to.

        `program_id:` Pubkey of the Token program that owns the accounts.
        Usually is TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
        
        #### Configuration Parameters Accepted:
        `encoding`, `commitment`, `min_context_slot`, `data_slice`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.DATA_SLICE,
            ConfigurationField.ENCODING,
            ConfigurationField.MIN_CONTEXT_SLOT,
        ])
        super().__init__(
            response_type = Response[list[TokenAccount]],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.TOKEN_ACCOUNTS_BY_DELEGATE
            ),
            configuration = configuration,
            account_delegate = account_delegate, #type:ignore
            mint = mint, #type:ignore
            program_id = program_id, #type:ignore
        )


    @model_validator(mode = "after")
    def check_data_slice_validity(self) -> Self:
        assert self.configuration, colored("self.configuration cannot be None.", "red")
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
        if self.mint is not None and self.program_id is not None:
            raise ValueError(
                colored(
                    "Specify either mint or program_id, not both.",
                    "light_red"
                )
            )
        if self.mint is None and self.program_id is None:
            raise ValueError(
                colored(
                    "You must specify either mint or program_id",
                    "light_red"
                )
            )
        return self


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[PublicKey | dict] = [self.account_delegate]
        
        if self.mint:
            parameters.append({"mint": self.mint})
        if self.program_id:
            parameters.append({"programId": self.program_id})

        return { **request, "params": self.add_configuration(parameters) }
