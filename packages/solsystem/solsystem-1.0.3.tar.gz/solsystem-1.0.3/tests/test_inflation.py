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
def client_provider(solana_endpoint: str) -> Generator[SyncClient, None, None]:
	with SyncClient(rpc_endpoint = cast(HttpUrl, solana_endpoint)) as client:
		yield client



def test_get_inflation_governor(client_provider: SyncClient):
	from SolSystem import (
		GetInflationGovernor, 
		InflationGovernor,
		Configuration,
		Commitment
    )

	response = client_provider.request(
		method = GetInflationGovernor()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[InflationGovernor].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetInflationGovernor(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetInflationGovernor(
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetInflationGovernor(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_inflation_rate(client_provider: SyncClient):
	from SolSystem import (
		GetInflationRate,
		InflationRate,
    )

	response = client_provider.request(
		method = GetInflationRate()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[InflationRate].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetInflationRate(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_inflation_reward(client_provider: SyncClient, account_key: str):
	from SolSystem import (
		GetInflationReward, 
		InflationReward,
		Configuration,
		Commitment
    )

	response = client_provider.request(
		method = GetInflationReward(
			addresses = ["6dmNQ5jwLeLk5REvio1JcMshcbvkYMwy26sJ8pbkvStu"],
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[InflationReward | None]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetInflationReward(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	
	response = client_provider.request(
		method = GetInflationReward(
			addresses = [account_key],
			configuration = Configuration(
				commitment = Commitment.CONFIRMED
            )
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetInflationReward(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	response = client_provider.request(
		method = GetInflationReward(
			addresses = [account_key],
			epoch = 3,
			configuration = Configuration(
				commitment = Commitment.FINALIZED
            )
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetInflationReward(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
