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



def test_get_epoch_info(client_provider: SyncClient):
	from SolSystem import (
		GetEpochInfo,
		EpochInfo,
		Commitment,
		Configuration,
    )

	response = client_provider.request(
		method = GetEpochInfo()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[EpochInfo].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetEpochInfo(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetEpochInfo(
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetEpochInfo(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_epoch_schedule(client_provider: SyncClient):
	from SolSystem import (
		GetEpochSchedule,
		EpochSchedule,
    )

	response = client_provider.request(
		method = GetEpochSchedule()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[EpochSchedule].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetEpochSchedule(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
