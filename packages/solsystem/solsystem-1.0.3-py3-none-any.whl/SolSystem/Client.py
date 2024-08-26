from __future__ import annotations
import time
import httpx
import asyncio
from typing import TypeVar
from pydantic import HttpUrl
from .Models.Common import Method


T = TypeVar("T")
type Seconds = float


class AsyncClient:
    base_rpc_url: HttpUrl
    session: httpx.AsyncClient
    global_headers: dict[str,str]
    between_request_time: Seconds
    
    _retry_curve: list[float] = [0.5, 1.0, 2.0, 3.0, 5.0]


    def __init__(
            self,
            rpc_endpoint: HttpUrl,
            between_request_time: Seconds = 0,
            global_headers: dict[str,str] | None = None,
            timeout: float = 10) -> None:
        """### Summary
        Solana Async Client.
        
        ### Parameters
        `rpc_endpoint:` URL to the RPC endpoint.

        `global_headers:` Headers to use for every subsequent request in this
        session.

        `between_request_time:` Allows you to set a static pause time before
        starting a request to make it easier to be Rate limit compliant.

        `timeout:` Default request timeout."""
        self.base_rpc_url = rpc_endpoint
        self.between_request_time = between_request_time
        
        self.global_headers = {"Content-Type": "application/json"}
        if global_headers is not None:
            self.global_headers = {** self.global_headers, ** global_headers}

        self.session = httpx.AsyncClient(timeout = timeout)

    

    async def request(self, method: Method[T]) -> T:
        if self.between_request_time > 0.0:
            await asyncio.sleep(self.between_request_time)

        for sleep_time in self._retry_curve:
            response = await self.session.post(
                url = str(self.base_rpc_url),
                json = method.model_dump(),
                headers = self.global_headers,
            )
            if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                await asyncio.sleep(sleep_time)
                continue
            
            if response.status_code != httpx.codes.OK:
                raise RuntimeError(F"Request failed with: {response.text}")
            break
                
        if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
            raise RuntimeError(
                "Exceeded acceptable retries and request still failed."
            )

        response = method.response_type(**response.json())
        if response.id != method.metadata.id:
            raise RuntimeError("Invalid id")
        return response

    
    async def __aenter__(self) -> AsyncClient:
        await self.session.__aenter__()
        return self
    

    async def __aexit__(self, _exception_type, _exception, _exception_traceback):
        await self.session.aclose()



class SyncClient:
    base_rpc_url: HttpUrl
    session: httpx.AsyncClient
    global_headers: dict[str,str]
    between_request_time: Seconds
    
    _retry_curve: list[float] = [0.5, 1.0, 2.0, 3.0, 5.0]


    def __init__(
            self,
            rpc_endpoint: HttpUrl,
            between_request_time: Seconds = 0,
            global_headers: dict[str,str] | None = None,
            timeout: float = 10) -> None:
        """### Summary
        Solana Async Client.
        
        ### Parameters
        `rpc_endpoint:` URL to the RPC endpoint.

        `global_headers:` Headers to use for every subsequent request in this
        session.

        `between_request_time:` Allows you to set a static pause time before
        starting a request to make it easier to be Rate limit compliant.

        `timeout:` Default request timeout."""
        self.base_rpc_url = rpc_endpoint
        self.between_request_time = between_request_time
        
        self.global_headers = {"Content-Type": "application/json"}
        if global_headers is not None:
            self.global_headers = {** self.global_headers, ** global_headers}

        self.session = httpx.Client(timeout = timeout)


    def request(self, method: Method[T]) -> T:
        if self.between_request_time > 0.0:
            time.sleep(self.between_request_time)

        for sleep_time in self._retry_curve:
            response = self.session.post(
                url = str(self.base_rpc_url),
                json = method.model_dump(),
                headers = self.global_headers,
            )
            if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                time.sleep(sleep_time)
                continue
            
            if response.status_code != httpx.codes.OK:
                raise RuntimeError(F"Request failed with: {response.text}")
            break
                
        if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
            raise RuntimeError(
                "Exceeded acceptable retries and request still failed."
            )

        response = method.response_type(**response.json())
        if response.id != method.metadata.id:
            raise RuntimeError("Invalid id")
        return response


    
    def __enter__(self) -> AsyncClient:
        self.session.__enter__()
        return self
    

    def __exit__(self, _exception_type, _exception, _exception_traceback):
        self.session.close()


