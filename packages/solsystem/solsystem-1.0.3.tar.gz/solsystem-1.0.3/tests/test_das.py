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


@pytest.fixture
def asset_id() -> str:
	return "3S8qX1MsMqRbiwKg2cQyx7nis1oHMgaCuc9c4VfvVdPN"
		


@pytest.fixture(scope = "module")
def client_provider(helius_endpoint: str) -> Generator[SyncClient, None, None]:
	with SyncClient(rpc_endpoint = cast(HttpUrl, helius_endpoint)) as client:
		yield client



def test_get_asset(client_provider: SyncClient, asset_id: str):
	from SolSystem import GetAsset, Asset

	response = client_provider.request(
		method = GetAsset(asset_id = asset_id)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Asset].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetAsset(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetAsset(
			asset_id = asset_id,
			show_fungible = True,
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetAsset(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	response = client_provider.request(
		method = GetAsset(
			asset_id = asset_id,
			show_fungible = True,
			show_inscription = True,
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetAsset(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	response = client_provider.request(
		method = GetAsset(
			asset_id = asset_id,
			show_inscription = True,
        )
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetAsset(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)