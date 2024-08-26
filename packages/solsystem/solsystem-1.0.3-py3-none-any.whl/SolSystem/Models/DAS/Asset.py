from __future__ import annotations
from typing import Literal, Any
from enum import StrEnum
from pydantic import (
    Field,
    AnyUrl,
    BaseModel,
    ConfigDict,
    field_validator,
)
from SolSystem.Models.Common import (
    UInt64,
    Float64,
    PublicKey,
)
from SolSystem.Models.DAS.HeliusAsset import (
    TokenInfo,
    MintExtensions,
    InscriptionDataAccount,
)



class Asset(BaseModel):
    """### Summary
    Metadata information about an asset. The structure is defined by metaplex
    API, but also supports additional fields as provided by helius API.

    ### Parameters
    Note, other parameters do not have well documented information on the
    metaplaex API reference and are thus left to the reader to parse.

    `burnt:` Whether this asset is burnt.

    `mutable:` Whether the asset metadata is mutable"""
    model_config = ConfigDict(extra = "allow")
    
    # Metaplex
    interface: Interface
    id: PublicKey
    content: AssetContent
    authorities: list[AssetAuthority]
    compression: AssetCompression
    creators: list[AssetCreator]
    grouping: list[AssetGroup]
    burnt: bool
    mutable: bool
    ownership: AssetOwnership
    royalty: AssetRoyalty
    supply: AssetSupply | None = None
    uses: AssetUses | None = None
    
    # Helius
    token_info: TokenInfo | None = None
    mint_extensions: MintExtensions | None = None
    inscription: InscriptionDataAccount | None = None
    spl20: Any | None = None




class Interface(StrEnum):
    """### Summary
    Interface type of the assets.
    [Reference](https://digital-asset-standard-api-js-docs.vercel.app/types/DasApiAssetInterface.html)."""
    V1_NFT = "V1_NFT"
    V1_PRINT = "V1_PRINT"
    LEGACY_NFT = "LEGACY_NFT"
    V2_NFT = "V2_NFT"
    FUNGIBLE_ASSET = "FungibleAsset"
    FUNGIBLE_TOKEN = "FungibleToken"
    CUSTOM = "Custom"
    IDENTITY = "Identity"
    EXECUTABLE = "Executable"
    PROGRAMMABLE_NFT = "ProgrammableNFT"



class AuthorityScope(StrEnum):
    FULL = "full"
    ROYALTY = "royalty"
    METADATA = "metadata"
    EXTENSION = "extension"



class MetadataAttribute(BaseModel):
    """### Summary
    Accepts extra arguments that are platform dependent. Metaplex expects
    only `trait_type` and `value`"""
    model_config = ConfigDict(extra = "allow")

    trait_type: str | None = None
    value: str | None = None



class AssetMetadata(BaseModel):
    """### Summary
    Accepts extra arguments that are platform dependent. Metaplex expects
    `description`,`name`,`symbol`,`token_standard`,`attributes`
    [reference](https://digital-asset-standard-api-js-docs.vercel.app/types/DasApiMetadata.html)"""
    model_config = ConfigDict(extra = "allow")

    description: str | None = None
    name: str | None = None
    symbol: str
    token_standard: str | None = None 
    attributes: list[MetadataAttribute] | None = None



class AssetAuthority(BaseModel):
    address: PublicKey
    scopes: list[AuthorityScope] = []



class ContentFiles(BaseModel):
    """### Summary
    File content only specifies mime and uri as expected fields, however
    there may be other information accepted. In helius for example there is a
    `cdn_uri`."""
    model_config = ConfigDict(extra = "allow")
    
    mime: str | None = None
    uri: AnyUrl | None = None



class AssetContent(BaseModel):
    """### Summary
    Content associated with this asset.
    
    ### Parameters
    `schema:` This field is specific to helius and is not defined in the
    metaplex documentation.
    
    `json_uri:` URL to json data for this content.
    
    `files:` Files associated with this Asset."""
    content_schema: str = Field(default = None, validation_alias = "$schema")
    json_uri: AnyUrl | None = None
    files: list[ContentFiles] | None = None
    metadata: AssetMetadata | None = None
    links: dict[str, AnyUrl] | None = None


    @field_validator("*", mode = "before")
    def prepare_empty_fields(cls, v: Any) -> Any:
        """### Summary
        Instead of NULL the API tends to return empty strings, so we handle that
        by converting to None in the pre validator"""
        if v == "":
            return None
        if v == {}:
            return None
        return v



class AssetCompression(BaseModel):
    asset_hash: PublicKey | None
    compressed: bool
    creator_hash: PublicKey | None
    data_hash: PublicKey | None
    eligible: bool
    leaf_id: UInt64
    seq: UInt64
    tree: PublicKey | None


    @field_validator("*", mode = "before")
    def prepare_empty_fields(cls, v: Any) -> Any:
        """### Summary
        Instead of NULL the API tends to return empty strings, so we handle that
        by converting to None in the pre validator"""
        if v == "": return None
        else: return v



class AssetCreator(BaseModel):
    address: PublicKey
    share: UInt64
    verified: bool



class AssetGroup(BaseModel):
    group_key: Literal["collection"]
    group_value: str



class OwnershipModel(StrEnum):
    SINGLE = "single"
    TOKEN = "token"


class AssetOwnership(BaseModel):
    delegate: PublicKey | None = None
    delegated: bool
    frozen: bool
    owner: PublicKey | None = None
    ownership_model: OwnershipModel

    # Helius
    supply: UInt64 | None = None
    mutable: bool | None = None
    burnt: bool | None = None


    @field_validator("*", mode = "before")
    def prepare_empty_fields(cls, v: Any) -> Any:
        """### Summary
        Instead of NULL the API tends to return empty strings, so we handle that
        by converting to None in the pre validator"""
        if v == "":
            return None
        return v



class RoyaltyModel(StrEnum):
    CREATORS = "creators"
    FANOUT = "fanout"
    SINGLE = "single"



class AssetRoyalty(BaseModel):
    basis_points: UInt64
    locked: bool
    percent: Float64
    primary_sale_happened: bool
    royalty_model: RoyaltyModel
    target: PublicKey | None = None



class AssetSupply(BaseModel):
    print_current_supply: UInt64
    print_max_supply: UInt64
    edition_nonce: UInt64 | None = None
    
    # Helius
    edition_number: UInt64 | None = None
    master_edition_mint: PublicKey | None = None



class UseMethod(StrEnum):
    BURN = "burn"
    MULTIPLE = "multiple"
    SINGLE = "single"


class AssetUses(BaseModel):
    remaining: UInt64
    total: UInt64
    use_method: UseMethod
