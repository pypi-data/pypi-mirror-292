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



def test_get_account_balance(client_provider: SyncClient, account_key: str):
	from SolSystem import GetAccountBalance, Lamports

	response = client_provider.request(
		method = GetAccountBalance(account = account_key)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Lamports].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetAccountBalance(account = account_key),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_account_info(client_provider: SyncClient, account_key: str):
	from SolSystem import GetAccountInfo, Account

	response = client_provider.request(
		method = GetAccountInfo(account = account_key)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Account].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetAccountInfo(account = account_key),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_largest_accounts(client_provider: SyncClient):
	"""This method is currently unsupported by rpc nodes."""
	pass
	# from SolSystem import GetLargestAccounts, AccountFilter, LargestAccount

	# response = client_provider.request(
	# 	method = GetLargestAccounts()
	# )
	# assert type(response).__name__ == "Response[list[LargestAccount]]", (
	# 	F"Invalid response type for this method: {type(response).__name__}"
	# )
	# assert response.value is not None, "Method must return largest account response"


	# response = client_provider.request(
	# 	method = GetLargestAccounts(account_filter = AccountFilter.CIRCULATING)
	# )
	# assert type(response).__name__ == "Response[list[LargestAccount]]", (
	# 	F"Invalid response type for this method: {type(response).__name__}"
	# )
	# assert response.value is not None, "Failed with AccountFilter.CIRCULATING"


	# response = client_provider.request(
	# 	method = GetLargestAccounts(account_filter = AccountFilter.NON_CIRCULATING)
	# )
	# assert type(response).__name__ == "Response[list[LargestAccount]]", (
	# 	F"Invalid response type for this method: {type(response).__name__}"
	# )
	# assert response.value is not None, "Failed with AccountFilter.NON_CIRCULATING"




def test_get_minimum_balance_for_rent_exemption(client_provider: SyncClient):
	from SolSystem import (
		GetMinimumBalanceForAccountRentExemption,
		Lamports,
	)

	response = client_provider.request(
		method = GetMinimumBalanceForAccountRentExemption(data_size = 20)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[Lamports].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetMinimumBalanceForAccountRentExemption(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	response = client_provider.request(
		method = GetMinimumBalanceForAccountRentExemption(data_size = 100)
	)
	assert response_type == expected_type, (
		F"Invalid response type for GetMinimumBalanceForAccountRentExemption(data_size = 100),"
		F"expected: {expected_type}, recieved: {response_type}"
	)
	assert response.model_dump()["result"] == 1586880, (
		"Expected result of 1586880 lamports for a data_size of 100"
	)



def test_get_multiple_accounts(client_provider: SyncClient):
	from SolSystem import GetMultipleAccounts, Account

	response = client_provider.request(
		method = GetMultipleAccounts(accounts = [
			"GpmCk8nzYdiYgTYHCiqS5eXRATE3VfUioQrM4SzmYtRV",
			"3X8kMwhoEETZv8U6eYAxk17EEr2LieA4BHeFtpgAjH8Z",
		])
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[Account]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetMultipleAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)


	response = client_provider.request(
		method = GetMultipleAccounts([
			"GpmCk8nzYdiYgTYHCiqS5eXRATE3VfUioQrM4SzmYtRV",
		])
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetMultipleAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)

	response = client_provider.request(
		method = GetMultipleAccounts([])
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetMultipleAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_program_accounts(client_provider: SyncClient):
	from SolSystem import GetProgramAccounts, ProgramAccount, DataSizeFilter

	response = client_provider.request(
		method = GetProgramAccounts(
			program = "4Nd1mBQtrMJVYVfKf2PJy9NZUZdTAsp7D4xWLs4gDB4T"
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[ProgramAccount]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetProgramAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)


	response = client_provider.request(
		method = GetProgramAccounts(
			program = "4Nd1mBQtrMJVYVfKf2PJy9NZUZdTAsp7D4xWLs4gDB4T",
			filters = [DataSizeFilter(data_size = 1080)]
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetProgramAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_vote_accounts(client_provider: SyncClient):
	from SolSystem import GetVoteAccounts, VoteAccounts

	response = client_provider.request(
		method = GetVoteAccounts()
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[VoteAccounts].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetVoteAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)


	response = client_provider.request(
		method = GetVoteAccounts(
			keep_unstaked_delinquents = True
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetVoteAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)