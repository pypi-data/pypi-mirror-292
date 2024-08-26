from __future__ import annotations
from pydantic import (
    Field,
    AnyUrl,
    BaseModel,
)
from SolSystem.Models.Common import (
    Int64,
    UInt8,
    UInt64,
    Float64,
    PublicKey,
)



class MintExtensions(BaseModel):
    """### Summary
    Non metaplex standard information as defined in helius
    [documentation](https://docs.helius.dev/compression-and-das-api/digital-asset-standard-das-api/get-asset#inscriptions-and-spl-20)"""
    confidential_transfer_mint      : ConfidentialTransferMint | None    = None
    confidential_transfer_fee_config: ConfidentialTransferFee | None     = None
    transfer_fee_config             : TransferFee | None                 = None
    metadata_pointer                : MetadataPointer | None             = None
    mint_close_authority            : MintCloseAuthority | None          = None
    permanent_delegate              : PermanentDelegate | None           = None
    transfer_hook                   : TransferHook | None                = None
    interest_bearing_config         : InterestBearing | None             = None
    default_account_state           : str | None                         = None
    confidential_transfer_account   : ConfidentialTransferAccount | None = None
    metadata                        : Metadata | None                    = None



class InscriptionDataAccount(BaseModel):
    """### Summary
    Non metaplex standard information as defined in helius
    [documentation](https://docs.helius.dev/compression-and-das-api/digital-asset-standard-das-api/get-asset#inscriptions-and-spl-20)"""
    order: UInt64 | None = None
    size: UInt64 | None = None
    content_type: str = Field(validation_alias = "contentType")
    encoding: str
    validation_hash: str = Field(validation_alias = "validationHash")
    inscription_data_account: str = Field(validation_alias = "inscriptionDataAccount")
    authority: PublicKey



class TokenInfo(BaseModel):
    """### Summary
    Non metaplex standard information as defined in helius
    [documentation](https://docs.helius.dev/compression-and-das-api/digital-asset-standard-das-api/get-asset#inscriptions-and-spl-20)"""
    symbol: str | None = None
    supply: UInt64
    decimals: UInt8
    token_program: PublicKey
    price_info: TokenPrice | None = None
    mint_authority: PublicKey | None = None
    freeze_authority: PublicKey | None = None



class TokenPrice(BaseModel):
    price_per_token: Float64
    currency: str



class ConfidentialTransferMint(BaseModel):
    authority: PublicKey
    auto_approve_new_accounts: bool
    auditor_elgamal_pubkey: PublicKey



class ConfidentialTransferFee(BaseModel):
    authority: PublicKey
    withdraw_withheld_authority_elgamal_pubkey: PublicKey
    harvest_to_mint_enabled: bool
    withheld_amounts: str



class OldTransferFee(BaseModel):
    epoch: PublicKey
    maximum_fee: str
    transfer_fee_basis_points: str


class NewTransferFee(BaseModel):
    epoch: PublicKey



class TransferFee(BaseModel):
    transfer_fee_config_authority: PublicKey
    withdraw_withheld_authority: PublicKey
    withheld_amount: UInt64
    older_transfer_fee: OldTransferFee
    newer_transfer_fee: NewTransferFee



class MetadataPointer(BaseModel):
    authority: PublicKey
    metadata_address: PublicKey



class MintCloseAuthority(BaseModel):
    close_authority: PublicKey



class PermanentDelegate(BaseModel):
    delegate: PublicKey



class TransferHook(BaseModel):
    authority: PublicKey
    program_id: PublicKey



class InterestBearing(BaseModel):
    rate_authority: PublicKey
    initialization_timestamp: Int64 | None = None
    pre_update_average_rate: UInt64 | None = None
    last_update_timestamp: Int64 | None = None
    current_rate: UInt64 | None = None



class ConfidentialTransferAccount(BaseModel):
    approved: bool
    elgamal_pubkey: PublicKey
    pending_balance_lo: str
    pending_balance_hi: str
    available_balance: str
    decryptable_available_balance: str
    allow_confidential_credits: bool
    allow_non_confidential_credits: bool
    pending_balance_credit_counter: UInt64 | None = None
    maximum_pending_balance_credit_counter: UInt64 | None = None
    expected_pending_balance_credit_counter: UInt64 | None = None
    actual_pending_balance_credit_counter: UInt64 | None = None



class Metadata(BaseModel):
    update_authority: PublicKey
    mint: PublicKey
    name: str
    symbol: str
    uri: AnyUrl
    additional_metadata: list[dict]