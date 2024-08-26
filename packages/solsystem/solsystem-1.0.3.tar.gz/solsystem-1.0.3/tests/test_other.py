import pytest
from pydantic import HttpUrl
from typing import cast, Generator
from SolSystem import (
	Response,
	SyncClient,
)	



@pytest.fixture(scope = "module")
def client_provider(solana_endpoint: str) -> Generator[SyncClient, None, None]:
	with SyncClient(rpc_endpoint = cast(HttpUrl, solana_endpoint)) as client:
		yield client



def test_get_fee_for_message(client_provider: SyncClient):
	from SolSystem import (
		GetFeeForMessage, 
		Configuration,
		Commitment,
		UInt64,
    )

	response = client_provider.request(
		method = GetFeeForMessage(message = (
			"AQABAgIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAA"
			"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
			"EBAQAA"
		))
	)
	assert response, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[UInt64 | None].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetInflationGovernor(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetFeeForMessage(message = (
				"AQABAgIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAA"
				"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
				"AAAAAAAAEBAQAA"
			),
			configuration = Configuration(
				commitment = Commitment.FINALIZED
            )
		)
	)
	assert response, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetInflationGovernor(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_genesis_hash(client_provider: SyncClient):
	from SolSystem import (
		GetGenesisHash,
		Base58Str,
    )

	response = client_provider.request(
		method = GetGenesisHash()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Base58Str].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetGenesisHash(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_leader_schedule(client_provider: SyncClient):
	from SolSystem import (
		GetLeaderSchedule,
		LeaderSchedule,
		Configuration,
		Commitment,
    )

	response = client_provider.request(
		method = GetLeaderSchedule()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[LeaderSchedule | None].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetLeaderSchedule(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetLeaderSchedule(
			slot = 280_657_769,
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetLeaderSchedule(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_recent_performance_samples(client_provider: SyncClient):
	from SolSystem import (
		GetRecentPerformanceSamples,
		PerformanceSample,
    )

	response = client_provider.request(
		method = GetRecentPerformanceSamples(limit = 10)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[PerformanceSample]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetRecentPerformanceSamples(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_supply(client_provider: SyncClient):
	from SolSystem import (
		GetSupply, 
		Supply,
		Configuration,
		Commitment
    )

	response = client_provider.request(
		method = GetSupply()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Supply].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetSupply(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetSupply(
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetSupply(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetSupply(
			exclude_non_circulating_accounts_list = True,
			configuration = Configuration(
				commitment = Commitment.FINALIZED
            )
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetSupply(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)