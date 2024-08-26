from __future__ import annotations

import json
from typing import Any
from types import TracebackType
from termcolor import cprint, colored
from websockets import (
	connect,
	ConnectionClosedOK,
	ConnectionClosedError,
	WebSocketClientProtocol,
)

from pydantic import WebsocketUrl
from SolSystem.Models.Common.Method import WsMethod
from SolSystem.Models.Common.Response import WsResponse


class ColoredException(BaseException):
	def __str__(self) -> str:
		return colored(super().__str__(), "red")



class SubscriptionFailedError(ColoredException):
	pass



class UnSubscriptionFailedError(ColoredException):
	pass



class MethodNotFoundError(ColoredException):
	pass



class MethodNotConnectedError(ColoredException):
	pass



class WebsocketMethod[T: WsResponse]:
	def __init__(
			self,
			method: WsMethod[T],
			connection_settings: dict[str, Any],
			parent: WebsocketClient,
			message_limit: int = -1
		) -> None:
		"""### Summary"""
		self.session: WebSocketClientProtocol | None = None
		self.method: WsMethod[T] = method
		self.unsubscribe_id: int | None = None
		self.parent = parent
		
		self.message_limit: int = message_limit
		self.message_count: int = 0

		self.connection_object: connect = connect(** connection_settings)


	async def connect(self) -> None:
		if self.session is None:
			self.session  = (
				await self.connection_object.__aenter__()
			)


	async def _disconnect(self) -> None:
		if self.session is not None:
			await self.connection_object.__aexit__(None, None, None)
			self.session = None
			return
		cprint("Attempted to disconnect session which wasn't connected.", "yellow")


	async def subscribe(self) -> None:
		if self.unsubscribe_id is not None:
			raise SubscriptionFailedError(
				F"This method is already subscribed to {self.method.metadata.method.name}"
			)
		
		await self.connect()
		if self.session is None:
			raise SubscriptionFailedError("Connection to websocket not established")
		
		cprint(self.method.model_dump_json(), "light_red")
		await self.session.send(message = self.method.model_dump_json())

		response: dict = json.loads(await self.session.recv())
		if (unsubscribe_id := response.get("result", None)) is not None:
			cprint(F"Subscribed - '{self.method.metadata.method.name}'", "green")
			self.unsubscribe_id = unsubscribe_id
			return
		
		if (error := response.get("error", None)) is not None:
			message = error.get("message", "")
			code = error.get("code", "")

			if message.lower() == "method not found":
				raise MethodNotFoundError(
					F"Code: {code} - The RPC endpoint does not support this method."
				)
			
		raise SubscriptionFailedError(
			"Subscription failed with error:\n"
			F"{json.dumps(response, indent = 2)}"
		)


	async def recieve(self) -> T:
		if self.session is None:
			raise MethodNotConnectedError()
		raw_return = await self.session.recv()
		cprint(json.dumps(json.loads(raw_return), indent = 2), "light_yellow")

		assert self.method, colored("self.method cannot be Null.", "red")
		return self.method.response_type(** json.loads(raw_return))


	def __aiter__(self) -> WebsocketMethod[T]:
		return self
	

	async def __anext__(self) -> T:
		try:
			if self.message_limit != -1:
				if self.message_count == self.message_limit:
					raise StopAsyncIteration
				self.message_count += 1
			return await self.recieve()
		
		except ConnectionClosedOK:
			self.unsubscribe_id = None
			self.message_count = 0
			raise StopAsyncIteration
		
		except ConnectionClosedError:
			self.unsubscribe_id = None
			self.message_count = 0
			raise StopAsyncIteration


	async def __aenter__(self) -> WebsocketMethod[T]:
		await self.connect()
		return self
	

	async def __aexit__(self, 
			_exception_type: type[BaseException] | None,
			_exception: BaseException | None,
			_traceback: TracebackType | None
		) -> None:
		assert self.connection_object, colored(
			"self.connection_object cannot be null at exit.", "red"
		)
		await self.unsubscribe()
		await self.connection_object.__aexit__(
			_exception_type,
			_exception,
			_traceback
		)


	async def unsubscribe(self) -> None:
		"""### Summary
		Unsubscribes this client instance from the current method. Will have no
		effect if there is no active subscription."""
		if self.unsubscribe_id is None or self.method is None:
			cprint("Ubsubscribe called without subscribing. No effect", "yellow")
			return
		
		if self.session is None:
			return
		
		await self.session.send(self.method.unsubscribe(self.unsubscribe_id))
		await self._disconnect()
		self.unsubscribe_id = None
		self.parent.connections.remove(self)
		
		cprint(F"Subscription Closed - '{self.method.metadata.method.name}'", "green")




class WebsocketClient:
	def __init__(
			self,
			end_point: WebsocketUrl,
			global_headers: dict[str,str] | None = None,
			user_agent: str | None = None,
			open_timeout: float = 10,
			close_timeout: float = 0,
			message_limit: int = -1,
		) -> None:
		"""### Summary
		Factory class for creating and managing Solana Websocket client 
		connections. Preferred usage is as a context manager handling a set of
		connection subscriptions.

		### Example

		```python
		async with WebsocketClient(
			end_point = <ws://url>,
			message_limit = 3
		) as client_pool:
			programs = await client_pool.subscribe(
				method = WsProgram(program = program)
			)
			async for message in programs:
				print(F"Recieved a message!: {message}")
		``` """
		self.message_limit = message_limit
		self.message_count = 0

		self.connections: list[WebsocketMethod] = []
		self.connection_settings = {
			"uri"              : str(end_point),
			"extra_headers"    : global_headers,
			"user_agent_header": user_agent,
			"open_timeout"     : open_timeout,
			"close_timeout"    : close_timeout,
		}


	async def unsubscribe_all(self) -> None:
		for connection in self.connections:
			await connection.unsubscribe()
			del connection
		self.connections = []


	async def subscribe[T: WsResponse](self, method: WsMethod[T]) -> WebsocketMethod[T]:
		"""### Summary
		Create a websocket subscription object with an active subscription to 
		the specified method. The lifecycle can then be managed either by the
		class itself or this parent instance. 

		### Example

		```python
		programs = await client_pool.subscribe(
			method = WsProgram(program = program)
		)
		async for message in programs:
			print(F"Recieved a message!: {message}")
		```
		
		### Parameters
		`method:` The websocket method to subscribe to initialized with needed
		arguments
		
		### Returns
		A WebsocketMethod connection class which holds the subscription to that
		particular endpoint."""
		method_instance = WebsocketMethod(
			method = method,
			connection_settings = self.connection_settings,
			parent = self,
			message_limit = self.message_limit,
		)
		await method_instance.connect()
		await method_instance.subscribe()
		self.connections.append(method_instance)
		return method_instance
	

	async def __aenter__(self) -> WebsocketClient:
		return self
	

	async def __aexit__(self, 
			_exception_type: type[BaseException] | None,
			_exception: BaseException | None,
			_traceback: TracebackType | None
		) -> None:
		await self.unsubscribe_all()

