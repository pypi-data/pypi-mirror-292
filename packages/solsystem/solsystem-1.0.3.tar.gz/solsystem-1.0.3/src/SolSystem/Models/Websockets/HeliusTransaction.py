from __future__ import annotations
from typing import Any
from pydantic import model_serializer

from SolSystem.Models.Transactions.Transaction import (
    TransactionDetail,
    TransactionEncoding,
)
from SolSystem.Models.Transactions.Transaction import Transaction
from SolSystem.Models.Common import (
    WsMethod,
    Base58Str,
    PublicKey,
    WsResponse,
    WsMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class WsGetTransaction(WsMethod[WsResponse[Transaction]]):
    include_vote: bool = False
    include_failed: bool = False
    signature: Base58Str | None = None
    include_accounts: list[PublicKey] | None = None
    exclude_accounts: list[PublicKey] | None = None
    required_accounts: list[PublicKey] | None = None
    
    show_rewards: bool = False
    encoding: TransactionEncoding | None = None
    transaction_details: TransactionDetail | None = None


    def __init__(
            self,
            include_vote: bool = False,
            include_failed: bool = False,
            signature: Base58Str | None = None,
            include_accounts: list[PublicKey] | None = None,
            exclude_accounts: list[PublicKey] | None = None,
            required_accounts: list[PublicKey] | None = None,
            show_rewards: bool = False,
            encoding: TransactionEncoding | None = None,
            transaction_details: TransactionDetail | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Tune in to real time Transaction updates when subscribed to a helius 
        rpc node. This method is not defined in the solana RPC docs, but exists
        as a third party implementation closely matching the official solana
        style.

        NOTE Only available on Helius RPC endpoints.
        NOTE Currently unavailable in mainnet Helius since the endpoint is in
        Beta
        
        ### Parameters
        `include_vote:` Include/exclude vote-related transactions 

        `include_failed:` include/exclude transactions that failed

        `signature:` Filters updates to a specific transaction based on its signature.

        `include_accounts:` A list of accounts for which you want to receive
        transaction updates. This means that only one of the accounts must be
        included in the transaction updates (e.g., Account 1 OR Account 2)

        `exclude_accounts:` A list of accounts you want to exclude from
        transaction updates.

        `required_accounts:` Transactions must involve these specified accounts
        to be included in updates. This means that all of the accounts must be
        included in the transaction updates (e.g., Account 1 AND Account 2).

        `show_rewards:` A boolean flag indicating if reward data should be
        included in the transaction updates.

        `encoding:` encoding format of the returned transaction data. 

        `transaction_details:` Determines the level of detail for the returned
        transaction data.

        #### Configuration Parameters Accepted:
        `max_supported_transaction_version`, `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field(
            name = "transaction_details",
            value = transaction_details,
        )
        configuration.add_extra_field(
            name = "encoding",
            value = encoding,
        )
        configuration.add_extra_field(
            name = "show_rewards",
            value = show_rewards,
        )
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
            ConfigurationField.MAX_SUPPORTED_TRANSACTION_VERSION,
        ])
        super().__init__(
            response_type = WsResponse[Transaction],
            metadata = MethodMetadata[WsMethodName](
                method = WsMethodName.HELIUS_TRANSACTION
            ),
            configuration       = configuration,
            include_vote        = include_vote,        #type:ignore
            include_failed      = include_failed,      #type:ignore
            signature           = signature,           #type:ignore
            include_accounts    = include_accounts,    #type:ignore
            exclude_accounts    = exclude_accounts,    #type:ignore
            required_accounts   = required_accounts,   #type:ignore
            show_rewards        = show_rewards,        #type:ignore
            encoding            = encoding,            #type:ignore
            transaction_details = transaction_details, #type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[dict] = [
            {
                "vote"           : self.include_vote,
                "failed"         : self.include_failed,
                "signature"      : self.signature,
                "accountInclude" : self.include_accounts,
                "accountExclude" : self.exclude_accounts,
                "accountRequired": self.required_accounts,
            }
        ]
        return { **request, "params": self.add_configuration(parameters) }
