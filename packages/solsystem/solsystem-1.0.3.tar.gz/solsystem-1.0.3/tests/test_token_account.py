import pytest
from pydantic import HttpUrl
from typing import cast, Generator
from SolSystem import (
	Response,
	SyncClient,
)	

# NOTE: For free plan RPC nodes, if specifying the program_id argument with the
# solana token program you will get an error since they do not cache it.


@pytest.fixture
def account_key() -> str:
	return "3X8kMwhoEETZv8U6eYAxk17EEr2LieA4BHeFtpgAjH8Z"
		


@pytest.fixture
def token_account() -> str:
	return "ApbBTwmieSmd5JtPHcRnd7g4tUWwcqdMoV5MBY4dAsWv"


@pytest.fixture
def token_mint() -> str:
	return "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"



@pytest.fixture(scope = "module")
def client_provider(helius_endpoint: str) -> Generator[SyncClient, None, None]:
	with SyncClient(rpc_endpoint = cast(HttpUrl, helius_endpoint)) as client:
		yield client



def test_get_token_account_balance(client_provider: SyncClient, token_account: str):
	from SolSystem import (
		GetTokenAccountBalance,
		Configuration,
		Commitment,
		TokenAmount,
    )

	response = client_provider.request(
		method = GetTokenAccountBalance(token_account = token_account)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[TokenAmount].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenAccountBalance(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetTokenAccountBalance(
			token_account = token_account,
			configuration = Configuration(
				commitment = Commitment.PROCESSED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenAccountBalance(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_token_accounts_by_delegate(client_provider: SyncClient, token_mint: str):
	from SolSystem import (
		GetTokenAccountsByDelegate,
		Configuration,
		Commitment,
		TokenAccount,
    )
	delegate = "4Nd1mBQtrMJVYVfKf2PJy9NZUZdTAsp7D4xWLs4gDB4T"
	response = client_provider.request(
		method = GetTokenAccountsByDelegate(
			account_delegate = delegate,
			mint = token_mint,
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[TokenAccount]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenAccountsByDelegate(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetTokenAccountsByDelegate(
			account_delegate = delegate,
			mint = token_mint,
			configuration = Configuration(
				commitment = Commitment.FINALIZED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenAccountsByDelegate(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_token_accounts_by_owner(client_provider: SyncClient, account_key: str):
	from SolSystem import (
		GetTokenAccountsByOwner,
		Configuration,
		TokenAccount,
		Commitment,
		Encoding,
    )
	response = client_provider.request(
		method = GetTokenAccountsByOwner(
			account = account_key,
			program_id = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
			configuration = Configuration(
				encoding = Encoding.BASE64
			)
		)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[TokenAccount]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenAccountsByOwner(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetTokenAccountsByOwner(
			account = account_key,
			program_id = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
			configuration = Configuration(
				commitment = Commitment.FINALIZED,
				encoding = Encoding.BASE64,
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenAccountsByOwner(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_token_largest_accounts(client_provider: SyncClient, token_mint: str):
	from SolSystem import (
		GetTokenLargestAccounts,
		Configuration,
		Commitment,
		TokenAmount,
    )
	response = client_provider.request(
		method = GetTokenLargestAccounts(mint = token_mint)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[list[TokenAmount]].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenLargestAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetTokenLargestAccounts(
			mint = token_mint,
			configuration = Configuration(
				commitment = Commitment.FINALIZED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenLargestAccounts(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)



def test_get_token_supply(client_provider: SyncClient, token_mint: str):
	from SolSystem import (
		GetTokenSupply,
		Configuration,
		Commitment,
		TokenAmount,
    )
	response = client_provider.request(
		method = GetTokenSupply(mint = token_mint)
	)
	assert response.value is not None, "Method must return a response"

	response_type = type(response).__name__
	expected_type = Response[TokenAmount].__name__
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenSupply(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)
	
	response = client_provider.request(
		method = GetTokenSupply(
			mint = token_mint,
			configuration = Configuration(
				commitment = Commitment.FINALIZED
            )
		)
	)
	assert response.value is not None, "Method must return a response"
	assert response_type == expected_type, (
		F"Invalid response type for GetTokenSupply(),"
		F" expected: {expected_type}, recieved: {response_type}"
	)