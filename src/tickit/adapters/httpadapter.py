import asyncio
import logging
from dataclasses import dataclass, field
from inspect import getmembers
from typing import Iterable

from aiohttp import web
from aiohttp.web_routedef import RouteDef

from tickit.adapters.interpreters.endpoints.http_endpoint import HttpEndpoint
from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device

LOGGER = logging.getLogger(__name__)


@dataclass
class HttpAdapter(Adapter):
    """An adapter implementation which delegates to a server and sets up endpoints.

    An adapter implementation which delegates the hosting of an http requests to a
    server and sets up the endpoints for said server.
    """

    host: str = "localhost"
    port: int = 8080

    _started: asyncio.Event = field(default_factory=asyncio.Event)
    _stopped: asyncio.Event = field(default_factory=asyncio.Event)

    async def run_forever(
        self, device: Device, raise_interrupt: RaiseInterrupt
    ) -> None:
        """Runs the server continuously."""
        await super().run_forever(device, raise_interrupt)

        await self._start_server()
        await self._stopped.wait()

    async def wait_until_ready(self, timeout: float = 1.0) -> None:
        """Blocks until server is ready to receive requests.

        Args:
            timeout: Raise a TimeoutError if the server is not ready within
                this many seconds. Defaults to 1.0
        """
        await asyncio.wait_for(self._started.wait(), timeout=timeout)

    async def stop(self) -> None:
        await self.site.stop()
        await self.app.shutdown()
        await self.app.cleanup()
        self._stopped.set()

    async def _start_server(self):
        LOGGER.debug(f"Starting HTTP server... {self}")
        self.app = web.Application()
        self.app.add_routes(list(self.endpoints()))
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.site = web.TCPSite(runner, host=self.host, port=self.port)
        await self.site.start()
        self._started.set()

    def endpoints(self) -> Iterable[RouteDef]:
        """Returns list of endpoints.

        Fetches the defined HTTP endpoints in the device adapter, parses them and
        then yields them.

        Returns:
            Iterable[HttpEndpoint]: The list of defined endpoints

        Yields:
            Iterator[Iterable[HttpEndpoint]]: The iterator of the defined endpoints
        """
        for _, func in getmembers(self):
            endpoint = getattr(func, "__endpoint__", None)  # type: ignore
            if endpoint is not None and isinstance(endpoint, HttpEndpoint):
                yield endpoint.define(func)
