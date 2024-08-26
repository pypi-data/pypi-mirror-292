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



def test_get_stake_activation(client_provider: SyncClient):
	from SolSystem import (
		GetStakeActivation,
		StakeActivation,
		Configuration,
		Commitment,
    )

	response = client_provider.request(
		method = GetStakeActivation(
			account = "DdUFmWoZQaQ7MmstfPWnkeCbDKuqXa8kZMMRT2diVVWN"
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[StakeActivation].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetStakeActivation(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	response = client_provider.request(
		method = GetStakeActivation(
			account = "DdUFmWoZQaQ7MmstfPWnkeCbDKuqXa8kZMMRT2diVVWN",
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetStakeActivation(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_stake_minimum_delegation(client_provider: SyncClient):
	from SolSystem import (
		GetStakeMinimumDelegation,
		Lamports,
		Configuration,
		Commitment,
    )

	response = client_provider.request(
		method = GetStakeMinimumDelegation()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Lamports].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetStakeMinimumDelegation(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	response = client_provider.request(
		method = GetStakeMinimumDelegation(
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetStakeMinimumDelegation(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)