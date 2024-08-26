from typing import Any
from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
    model_serializer,
)
from SolSystem.Models.DAS.HeliusAccount import HeliusTokenAccounts
from SolSystem.Models.Common import (
    Method,
    Response,
    PublicKey,
    DasMethodName,
    Configuration,
    MethodMetadata,
)



class DisplayOptions(BaseModel):
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True
    )
    show_zero_balance: bool | None = None



class GetTokenAccounts(Method[Response[HeliusTokenAccounts]]):
    def __init__(
            self,
            mint: PublicKey,
            owner: PublicKey | None = None,
            limit: int = 100,
            page: int | None = None,
            cursor: str | None = None,
            before: str | None = None,
            after: str | None = None,
            show_zero_balance: bool = False,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns all token accounts for a particular asset mint. This method
        uses a cursor for pagination. Pass the cursor back to the method to
        continue returning all accounts.
    
        ### Parameters
        `mint:` The token mint public key.

        `owner:` Optionally filter by an owner key.

        `limit:` How many tokens to return per page.

        `page:` Return a particular page of the paginated data.

        `cursor:` The continuation cursor for pagination. The cursor object will
        be empty in the response when pagination is complete.
        
        `before:` Return data from before this cursor

        `after:` Return data from after this cursor
        
        `show_zero_balance:` Show or hide accounts with zero token balance.

        #### Configuration Parameters Accepted:"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field(
            "display_options",
            DisplayOptions(show_zero_balance = show_zero_balance)
        )
        configuration.add_extra_field(name = "mint", value = mint)
        configuration.add_extra_field(name = "owner", value = owner)
        configuration.add_extra_field(name = "limit", value = limit)
        configuration.add_extra_field(name = "page", value = page)
        configuration.add_extra_field(name = "cursor", value = cursor)
        configuration.add_extra_field(name = "before", value = before)
        configuration.add_extra_field(name = "after", value = after)
        configuration.filter_for_accepted_parameters([])

        super().__init__(
            response_type = Response[HeliusTokenAccounts],
            metadata = MethodMetadata[DasMethodName](
                method = DasMethodName.GET_TOKEN_ACCOUNTS
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        """### Summary
        Note that for DAS rpc calls (on helius at least) the format for the
        params object becomes a dictionary instead of a list as is in the
        typical solana RPC call structure."""
        request = self.metadata.model_dump()
        return { **request, "params": self.add_configuration({}) }
