from typing import Any
from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
    model_serializer,
)
from SolSystem.Models.DAS.Asset import Asset
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
    
    show_fungible: bool | None = None
    show_inscription: bool | None = None



class GetAsset(Method[Response[Asset]]):
    def __init__(
            self,
            asset_id: PublicKey,
            show_fungible: bool | None = None,
            show_inscription: bool | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns details for a particular asset id as defined by the metaplex
        standard. Implementations may differ based on RPC provider.
    
        ### Parameters
        `asset_id:` Asset ID can be an NFT ID or a mint account ID for a token.

        `show_fungible:` (HELIUS) Return additional details about fungible token.

        `show_inscription:` (HELIUS) Show inscription and SPL20 token data in
        response.

        #### Configuration Parameters Accepted:"""
        if not configuration:
            configuration = Configuration()

        if show_fungible is not None or show_inscription is not None:
            configuration.add_extra_field(
                "display_options",
                DisplayOptions(
                    show_fungible = show_fungible,
                    show_inscription = show_inscription,
                )
            )
        configuration.add_extra_field("id", asset_id)
        configuration.filter_for_accepted_parameters([])
        super().__init__(
            response_type = Response[Asset],
            metadata = MethodMetadata[DasMethodName](
                method = DasMethodName.ASSET
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
