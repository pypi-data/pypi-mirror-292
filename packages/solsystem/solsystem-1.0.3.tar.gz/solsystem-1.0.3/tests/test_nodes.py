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



def test_get_cluster_nodes(client_provider: SyncClient):
	from SolSystem import (
		GetClusterNodes,
		ClusterNode,
    )

	response = client_provider.request(
		method = GetClusterNodes()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[ClusterNode]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetClusterNodes(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)




def test_get_node_health(client_provider: SyncClient):
	from typing import Literal
	from SolSystem import (
		GetNodeHealth,
    )

	response = client_provider.request(
		method = GetNodeHealth()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Literal["ok"]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetNodeHealth(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_node_identity(client_provider: SyncClient):
	from SolSystem import (
		GetNodeIdentity,
		NodeIdentity,
    )

	response = client_provider.request(
		method = GetNodeIdentity()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[NodeIdentity].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetNodeIdentity(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_node_version(client_provider: SyncClient):
	from SolSystem import (
		GetNodeVersion,
		NodeVersion,
    )

	response = client_provider.request(
		method = GetNodeVersion()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[NodeVersion].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetNodeVersion(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)