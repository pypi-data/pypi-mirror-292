from typing import Any
from pydantic import model_serializer
from SolSystem.Models.Accounts.VoteAccount import VoteAccounts
from SolSystem.Models.Common import (
    UInt64,
    Method,
    Response,
    Base58Str,
    RPCMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)


class GetVoteAccounts(Method[Response[VoteAccounts]]):
    def __init__(
            self,
            validator_vote_address: Base58Str | None = None,
            keep_unstaked_delinquents: bool | None = None,
            delinquent_slot_distance: UInt64 | None = None,
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Returns the account info and associated stake for all the voting
        accounts in the current bank.
        
        ### Parameters
        `validator_vote_address:` Only return results for this validator vote
        address

        `keep_unstaked_delinquents:` If set to true, do not filter out delinquent
        validators with no stake

        `delinquent_slot_distance:` Specify the number of slots behind the tip
        that a validator must fall to be considered delinquent. For the sake of
        consistency between ecosystem products, it is *not* recommended that this
        argument be specified.

        #### Configuration Parameters Accepted:
        `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.add_extra_field("vote_pubkey", validator_vote_address)
        configuration.add_extra_field(
            "keep_unstaked_delinquents",
            keep_unstaked_delinquents,
        )
        configuration.add_extra_field(
            "delinquent_slot_distance",
            delinquent_slot_distance,
        )
        configuration.filter_for_accepted_parameters([
            ConfigurationField.COMMITMENT,
        ])

        super().__init__(
            response_type = Response[VoteAccounts],
            metadata = MethodMetadata[RPCMethodName](
                method = RPCMethodName.VOTE_ACCOUNTS
            ),
            configuration = configuration,
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = []
        
        return { **request, "params": self.add_configuration(parameters) }
