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



def test_get_highest_snapshot_slot(client_provider: SyncClient):
	from SolSystem import (
		GetHighestSnapshotSlot,
		SnapshotSlot,
		
    )

	response = client_provider.request(
		method = GetHighestSnapshotSlot()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[SnapshotSlot].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetHighestSnapshotSlot(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_max_retransmit_slot(client_provider: SyncClient):
	from SolSystem import (
		GetMaxRetransmitSlot,
		UInt64,
    )

	response = client_provider.request(
		method = GetMaxRetransmitSlot()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[UInt64].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetMaxRetransmitSlot(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_max_shred_insert_slot(client_provider: SyncClient):
	from SolSystem import (
		GetMaxShredInsertSlot,
		UInt64,
    )

	response = client_provider.request(
		method = GetMaxShredInsertSlot()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[UInt64].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetMaxShredInsertSlot(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_slot(client_provider: SyncClient):
	from SolSystem import (
		GetSlot,
		Configuration,
		Commitment,
		UInt64,
    )

	response = client_provider.request(
		method = GetSlot()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[UInt64].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetSlot(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetSlot(
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetSlot(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_slot_leader(client_provider: SyncClient):
	from SolSystem import (
		GetSlotLeader,
		Configuration,
		Commitment,
		PublicKey,
    )

	response = client_provider.request(
		method = GetSlotLeader()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[PublicKey].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetSlotLeader(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetSlotLeader(
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetSlotLeader(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_slot_leaders(client_provider: SyncClient):
	from SolSystem import (
		GetSlotLeaders,
		Configuration,
		Commitment,
		PublicKey,
    )

	response = client_provider.request(
		method = GetSlotLeaders(
			start_slot = 280612057,
			limit = 200,
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[PublicKey]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetSlotLeaders(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetSlotLeaders(
			start_slot = 280603057,
			limit = 30,
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetSlotLeaders(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	response = client_provider.request(
		method = GetSlotLeaders(
			start_slot = 280612057,
			limit = 200,
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetSlotLeaders(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_minimum_ledger_slot(client_provider: SyncClient):
	from SolSystem import (
		GetMinimumLedgerSlot,
		UInt64,
    )

	response = client_provider.request(
		method = GetMinimumLedgerSlot()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[UInt64].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetMinimumLedgerSlot(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
