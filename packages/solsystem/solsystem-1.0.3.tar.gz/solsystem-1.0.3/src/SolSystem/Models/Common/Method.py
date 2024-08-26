from __future__ import annotations

import abc
import json
import random
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Generic, TypeVar, Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic.alias_generators import to_camel

from SolSystem.Models.Common.Configuration import Configuration
from SolSystem.Models.Common.DataTypes import UInt32
from SolSystem.Models.Common.Response import RpcVersion, Response, WsResponse


class RPCMethodName(StrEnum):
	ACCOUNT_INFO                       = "getAccountInfo"
	BALANCE                            = "getBalance"
	BLOCK                              = "getBlock"
	BLOCK_COMMITMENT                   = "getBlockCommitment"
	BLOCK_HEIGHT                       = "getBlockHeight"
	BLOCK_PRODUCTION                   = "getBlockProduction"
	BLOCK_TIME                         = "getBlockTime"
	BLOCKS                             = "getBlocks"
	BLOCKS_WITH_LIMIT                  = "getBlocksWithLimit"
	CLUSTER_NODES                      = "getClusterNodes"
	EPOCH_INFO                         = "getEpochInfo"
	EPOCH_SCHEDULE                     = "getEpochSchedule"
	FEE_FOR_MESSAGE                    = "getFeeForMessage"
	FIRST_AVAILABLE_BLOCK              = "getFirstAvailableBlock"
	GENESIS_HASH                       = "getGenesisHash"
	HEALTH                             = "getHealth"
	HIGHEST_SNAPSHOT_SLOT              = "getHighestSnapshotSlot"
	IDENTITY                           = "getIdentity"
	INFLATION_GOVERNOR                 = "getInflationGovernor"
	INFLATION_RATE                     = "getInflationRate"
	INFLATION_REWARD                   = "getInflationReward"
	LARGEST_ACCOUNTS                   = "getLargestAccounts"
	LATEST_BLOCKHASH                   = "getLatestBlockhash"
	LEADER_SCHEDULE                    = "getLeaderSchedule"
	MAX_RETRANSMIT_SLOT                = "getMaxRetransmitSlot"
	MAX_SHRED_INSERT_SLOT              = "getMaxShredInsertSlot"
	MINIMUM_BALANCE_FOR_RENT_EXEMPTION = "getMinimumBalanceForRentExemption"
	MULTIPLE_ACCOUNTS                  = "getMultipleAccounts"
	PROGRAM_ACCOUNTS                   = "getProgramAccounts"
	RECENT_PERFORMANCE_SAMPLES         = "getRecentPerformanceSamples"
	RECENT_PRIORITIZATION_FEES         = "getRecentPrioritizationFees"
	SIGNATURE_STATUSES                 = "getSignatureStatuses"
	SIGNATURES_FOR_ADDRESS             = "getSignaturesForAddress"
	SLOT                               = "getSlot"
	SLOT_LEADER                        = "getSlotLeader"
	SLOT_LEADERS                       = "getSlotLeaders"
	STAKE_ACTIVATION                   = "getStakeActivation"
	STAKE_MINIMUM_DELEGATION           = "getStakeMinimumDelegation"
	SUPPLY                             = "getSupply"
	TOKEN_ACCOUNT_BALANCE              = "getTokenAccountBalance"
	TOKEN_ACCOUNTS_BY_DELEGATE         = "getTokenAccountsByDelegate"
	TOKEN_ACCOUNTS_BY_OWNER            = "getTokenAccountsByOwner"
	TOKEN_LARGEST_ACCOUNTS             = "getTokenLargestAccounts"
	TOKEN_SUPPLY                       = "getTokenSupply"
	TRANSACTION                        = "getTransaction"
	TRANSACTION_COUNT                  = "getTransactionCount"
	VERSION                            = "getVersion"
	VOTE_ACCOUNTS                      = "getVoteAccounts"
	IS_BLOCKHASH_VALID                 = "isBlockhashValid"
	MINIMUM_LEDGER_SLOT                = "minimumLedgerSlot"
	REQUEST_AIRDROP                    = "requestAirdrop"
	SEND_TRANSACTION                   = "sendTransaction"
	SIMULATE_TRANSACTION               = "simulateTransaction"



class DasMethodName(StrEnum): 
	ASSET = "getAsset"
	GET_TOKEN_ACCOUNTS = "getTokenAccounts"



@dataclass
class WsMethodNameMixin:
	subscribe: str
	unsubscribe: str



class WsMethodName(WsMethodNameMixin, Enum): 
	ACCOUNT            = "accountSubscribe",      "accountUnsubscribe"
	BLOCK              = "blockSubscribe",        "blockUnsubscribe"
	LOGS               = "logsSubscribe",         "logsUnsubscribe"
	PROGRAM            = "programSubscribe",      "programUnsubscribe"
	ROOT               = "rootSubscribe",         "rootUnsubscribe"
	SIGNATURE          = "signatureSubscribe",    "signatureUnsubscribe"
	SLOT               = "slotSubscribe",         "slotUnsubscribe"
	SLOTS_UPDATES      = "slotsUpdatesSubscribe", "slotsUpdatesUnsubscribe"
	VOTE               = "voteSubscribe",         "voteUnsubscribe"
	HELIUS_TRANSACTION = "transactionSubscribe",  "transactionUnsubscribe"



MethodName = TypeVar("MethodName", RPCMethodName, DasMethodName, WsMethodName)
class MethodMetadata(BaseModel, Generic[MethodName]):
	"""### Summary
	Metadata information sent with every request method. The generic MethodName
	is used to send the correct metadata name depending on RPC, DAS, or 
	Websockets.
	
	### Parameters
	```python
	jsonrpc: RpcVersion = "2.0"
	id: UInt32 = Field(default_factory = lambda: random.randint(1, (2**31 - 1)))
	method: MethodName
	```"""
	jsonrpc: RpcVersion = "2.0"
	id: UInt32 = Field(default_factory = lambda: random.randint(1, (2**31 - 1)))
	method: MethodName

	@field_serializer("method")
	def serialize_method_name(self, method: MethodName) -> str:
		if isinstance(method, WsMethodName):
			return method.subscribe
		return method.value



MethodResponse = TypeVar("MethodResponse", bound = Response)
class Method(BaseModel, abc.ABC, Generic[MethodResponse]):
	"""### Summary
	Base class for a solana API Method. Accepts a generic response type which
	is used to construct the response object and a RPC or DAS method metadata.
	
	### Paramters
	```python
	response_type : type[MethodResponse] = Field(exclude = True)
	metadata      : MethodMetadata[RPCMethodName] | MethodMetadata[DasMethodName]
	configuration : Configuration | None = None
	```"""
	model_config = ConfigDict(alias_generator = to_camel, populate_by_name = True)

	response_type : type[MethodResponse] = Field(exclude = True)
	metadata      : MethodMetadata[RPCMethodName] | MethodMetadata[DasMethodName]
	configuration : Configuration | None = None


	def add_configuration(self, parameters: list[Any] | dict) -> list[Any] | dict:
		if self.configuration:
			options = self.configuration.model_dump(
				exclude_none = True,
				by_alias = True,
			)
			if options:
				if isinstance(parameters, dict):
					parameters.update(options)
				else:
					parameters.append(options)
		return parameters



WsMethodResponse = TypeVar("WsMethodResponse", bound = WsResponse)
class WsMethod(BaseModel, abc.ABC, Generic[WsMethodResponse]):
	"""### Summary
	Base class for a solana API Websocket Method. Accepts a generic response
	type which is used to construct the response object and a websocket method
	metadata. Unlike the regular `Method` object, the websocket method also
	has a unsubscribe() function dependant on the specified method metadata.
	
	### Parameters
	```python
	response_type : type[WsMethodResponse] = Field(exclude = True)
	metadata      : MethodMetadata[WsMethodName]
	configuration : Configuration | None = None
	```"""
	model_config = ConfigDict(alias_generator = to_camel, populate_by_name = True)

	response_type : type[WsMethodResponse] = Field(exclude = True, frozen = True)
	metadata      : MethodMetadata[WsMethodName]
	configuration : Configuration | None = None


	def unsubscribe(self, unsubscribe_id: int) -> str:
		return json.dumps({
			"jsonrpc": "2.0",
			"id": self.metadata.id,
			"method": self.metadata.method.unsubscribe,
			"params": [unsubscribe_id]
		})
	

	def add_configuration(self, parameters: list[Any]) -> list[Any]:
		if self.configuration:
			options = self.configuration.model_dump(
				exclude_none = True,
				by_alias = True,
			)
			if options:
				parameters.append(options)
		return parameters