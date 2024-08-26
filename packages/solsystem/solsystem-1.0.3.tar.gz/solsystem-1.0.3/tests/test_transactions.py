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
def transaction_sig() -> str:
	return "5YDL3kwU8kxyCe12ewwBA5H9f8HU3gSBAkgqoV3v9K9cm8CkY73t8niYayKH7uTQbR2xSX7pb9Xn37DeaXCCkrXL"



@pytest.fixture(scope = "module")
def client_provider(helius_endpoint: str) -> Generator[SyncClient, None, None]:
	with SyncClient(rpc_endpoint = cast(HttpUrl, helius_endpoint)) as client:
		yield client



def test_get_signatures_for_address(client_provider: SyncClient, account_key: str):
	from SolSystem import (
		GetSignaturesForAddress,
		TransactionSignature,
		Configuration,
		Commitment,
    )

	response = client_provider.request(
		method = GetSignaturesForAddress(
			account = account_key,
			limit = 12,
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[TransactionSignature]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetSignaturesForAddress(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetSignaturesForAddress(
			account = account_key,
			limit = 3,
			configuration = Configuration(
				commitment = Commitment.CONFIRMED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetSignaturesForAddress(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)




def test_get_signature_statuses(client_provider: SyncClient, transaction_sig: str):
	from SolSystem import (
		GetSignatureStatus,
		SignatureStatus,
		Configuration,
		Commitment,
    )
	response = client_provider.request(
		method = GetSignatureStatus(transaction_signatures = [transaction_sig])
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[SignatureStatus | None]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetSignatureStatus(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetSignatureStatus(
			transaction_signatures = [transaction_sig],
			search_transaction_history = True,
			configuration = Configuration(
				commitment = Commitment.FINALIZED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetSignatureStatus(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_transaction(client_provider: SyncClient, transaction_sig: str):
	from SolSystem import (
		GetTransaction,
		Transaction,
		Configuration,
		Commitment,
    )
	response = client_provider.request(
		method = GetTransaction(
			transaction_signature = transaction_sig,
			configuration = Configuration(
				max_supported_transaction_version = 0
			),
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Transaction | None].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetTransaction(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetTransaction(
			transaction_signature = transaction_sig,
			configuration = Configuration(
				commitment = Commitment.FINALIZED,
				max_supported_transaction_version = 0
            ),
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetTransaction(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_transaction_count(client_provider: SyncClient):
	from SolSystem import (
		GetTransactionCount,
		UInt64,
		Configuration,
		Commitment,
    )
	response = client_provider.request(
		method = GetTransactionCount()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[UInt64].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetTransactionCount(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetTransactionCount(
			configuration = Configuration(
				commitment = Commitment.FINALIZED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetTransactionCount(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_request_airdrop(client_provider: SyncClient):
	pass



def test_send_transaction(client_provider: SyncClient):
	pass



def test_simulate_transaction(client_provider: SyncClient):
	pass