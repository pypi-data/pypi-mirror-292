import pytest
from pydantic import HttpUrl
from typing import cast, Generator
from SolSystem import (
	Response,
	SyncClient,
)	


@pytest.fixture
def account_key() -> str:
	return "3X8kMwhoEETZv8U6eYAxk17EEr2LieA4BHeFtpgAjH8Z"
		


@pytest.fixture(scope = "module")
def client_provider(helius_endpoint: str) -> Generator[SyncClient, None, None]:
	with SyncClient(rpc_endpoint = cast(HttpUrl, helius_endpoint)) as client:
		yield client



def test_get_block(client_provider: SyncClient):
	from SolSystem import GetBlock, Block, TransactionDetail, Configuration

	response = client_provider.request(
		method = GetBlock(
			slot_number = 172_410_213,
			configuration = Configuration(
				max_supported_transaction_version = 0
			)
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Block].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetBlock(slot_number = 172_410_213),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlock(
			slot_number = 172_410_213,
			transaction_details = TransactionDetail.ACCOUNTS,
			configuration = Configuration(
				max_supported_transaction_version = 0
			)
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlock(slot_number = 172_410_213),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlock(
			slot_number = 182_410_213,
			transaction_details = TransactionDetail.NONE,
			configuration = Configuration(
				max_supported_transaction_version = 0
			)
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlock(slot_number = 182_410_213),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlock(
			slot_number = 182_410_213,
			transaction_details = TransactionDetail.SIGNATURES,
			configuration = Configuration(
				max_supported_transaction_version = 0
			)
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlock(slot_number = 182_410_213),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlock(
			slot_number = 182_413_213,
			rewards = True,
			configuration = Configuration(
				max_supported_transaction_version = 0
			)
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlock(slot_number = 182_413_213),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	


def test_get_block_commitment(client_provider: SyncClient):
	from SolSystem import GetBlockCommitment, BlockCommitment

	response = client_provider.request(
		method = GetBlockCommitment(block_number = 102_413_213)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[BlockCommitment].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetBlockCommitment(block_number = 102_413_213),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlockCommitment(block_number = 102_013_213)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlockCommitment(block_number = 102_413_213),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	


def test_get_block_height(client_provider: SyncClient):
	from SolSystem import GetBlockHeight, UInt64, Configuration, Commitment

	response = client_provider.request(
		method = GetBlockHeight()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[UInt64].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetBlockHeight,"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlockHeight(
			configuration = Configuration(commitment = Commitment.PROCESSED)
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlockHeight(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	


def test_get_block_production(client_provider: SyncClient):
	from SolSystem import GetBlockProduction, SlotRange, BlockProduction

	response = client_provider.request(
		method = GetBlockProduction()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[BlockProduction].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetBlockProduction(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlockProduction(
			slot_range = SlotRange(
				first_slot = 123_213_213,
				last_slot = 123_213_313,
			)
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlockProduction(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	


def test_get_blocks(client_provider: SyncClient):
	from SolSystem import GetBlocks, UInt64

	response = client_provider.request(
		method = GetBlocks(start_slot = 123_213_213, end_slot = 123_213_213)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[UInt64]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetBlocks(start_slot = 123_213_213, end_slot = 123_213_214),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlocks(start_slot = 123_413_213, end_slot = 123_413_413)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlocks(start_slot = 123_413_213, end_slot = 123_413_413),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	


def test_get_blocks_with_limit(client_provider: SyncClient):
	from SolSystem import GetBlocksWithLimit, UInt64

	response = client_provider.request(
		method = GetBlocksWithLimit(start_slot = 122_413_213, limit = 200)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[UInt64]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetBlocksWithLimit(start_slot = 122_413_213, limit = 200),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetBlocksWithLimit(start_slot = 122_500_213, limit = 1000)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetBlocksWithLimit(start_slot = 122_500_213, limit = 1000),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	


def test_get_block_time(client_provider: SyncClient):
	from SolSystem import GetBlockTime, Int64

	response = client_provider.request(
		method = GetBlockTime(block_number = 122_413_213)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Int64].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetBlockTime(block_number = 122_413_213),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	


def test_get_first_available_block(client_provider: SyncClient):
	from SolSystem import GetFirstAvailableBlock, UInt64

	response = client_provider.request(
		method = GetFirstAvailableBlock()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[UInt64].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetFirstAvailableBlock(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	


def test_get_latest_blockhash(client_provider: SyncClient):
	from SolSystem import (
		GetLatestBlockhash,
		LatestBlockhash,
		Configuration,
		Commitment,
	)

	response = client_provider.request(
		method = GetLatestBlockhash()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[LatestBlockhash].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetLatestBlockhash(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetLatestBlockhash(
			configuration = Configuration(commitment = Commitment.PROCESSED)
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetLatestBlockhash(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_recent_prioritization_fees(client_provider: SyncClient, account_key: str):
	from SolSystem import (
		GetRecentPrioritizationFees,
		PrioritizationFee,
	)

	response = client_provider.request(
		method = GetRecentPrioritizationFees()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[PrioritizationFee]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetRecentPrioritizationFees(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetRecentPrioritizationFees(accounts = [account_key])
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetRecentPrioritizationFees(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_is_blockhash_valid(client_provider: SyncClient):
	from SolSystem import (
		IsBlockhashValid,
		Configuration,
		Commitment,
	)

	response = client_provider.request(
		method = IsBlockhashValid(
			blockhash = "J7rBdM6AecPDEZp8aPq5iPSNKVkU5Q76F3oAV4eW5wsW"
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[bool].__name__
	assert response_type == expected_type, (
		F"Invalid response type for IsBlockhashValid(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = IsBlockhashValid(
			blockhash = "J7rBdM6AecPDEZp8aPq5iPSNKVkU5Q76F3oAV4eW5wsW",
			configuration = Configuration(commitment = Commitment.CONFIRMED)
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for IsBlockhashValid(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
