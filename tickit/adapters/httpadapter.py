from dataclasses import dataclass
from inspect import getmembers
from typing import AsyncIterable, Awaitable, Callable, Iterable, Optional, TypeVar

from aiohttp import web

from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.servers.http import HTTPServer
from tickit.core.device import Device

#: Message type
T = TypeVar("T")


@dataclass
class HTTPAdapter:
    """An adapter implementation which delegates to a server ....

    An adapter implementation which delegates the hosting of an external messaging
    protocol to a server and ....
    """

    _device: Device
    _raise_interrupt: Callable[[], Awaitable[None]]
    _server: HTTPServer

    async def run_forever(self) -> None:
        """Runs the server continously."""

        self._server.app.add_routes(list(self.endpoints()))

        await self._server.run_forever()

    def endpoints(self) -> Iterable[HTTPEndpoint]:

        for _, func in getmembers(self):
            endpoint = getattr(func, "__endpoint__", None)
            if endpoint is not None:
                yield endpoint.parse(func)
