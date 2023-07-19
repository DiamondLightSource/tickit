import asyncio
import logging
from dataclasses import dataclass
from inspect import getmembers
from typing import Awaitable, Callable, Iterable, Optional, TypeVar

from aiohttp import web
from aiohttp.web_routedef import RouteDef

from tickit.adapters.interpreters.endpoints.http_endpoint import HttpEndpoint
from tickit.core.adapter import Adapter, RaiseInterrupt

LOGGER = logging.getLogger(__name__)

#: Device type
D = TypeVar("D")


@dataclass
class HttpAdapter(Adapter[D]):
    """An adapter implementation which delegates to a server and sets up endpoints.

    An adapter implementation which delegates the hosting of an http requests to a
    server and sets up the endpoints for said server.
    """

    host: str = "localhost"
    port: int = 8080

    _stopped: Optional[asyncio.Event] = None
    _ready: Optional[asyncio.Event] = None

    async def run_forever(self, device: D, raise_interrupt: RaiseInterrupt) -> None:
        """Runs the server continuously."""
        await super().run_forever(device, raise_interrupt)

        self._ensure_stopped_event().clear()
        await self._start_server()
        self._ensure_ready_event().set()
        try:
            await self._ensure_stopped_event().wait()
        except asyncio.CancelledError:
            await self.stop()

    async def wait_until_ready(self, timeout: float = 1.0) -> None:
        while self._ready is None:
            await asyncio.sleep(0.1)
        await asyncio.wait_for(self._ready.wait(), timeout=timeout)

    async def stop(self) -> None:
        stopped = self._ensure_stopped_event()
        if not stopped.is_set():
            await self.site.stop()
            await self.app.shutdown()
            await self.app.cleanup()
            self._ensure_stopped_event().set()
        if self._ready is not None:
            self._ready.clear()

    def _ensure_stopped_event(self) -> asyncio.Event:
        if self._stopped is None:
            self._stopped = asyncio.Event()
        return self._stopped

    def _ensure_ready_event(self) -> asyncio.Event:
        if self._ready is None:
            self._ready = asyncio.Event()
        return self._ready

    async def _start_server(self):
        LOGGER.debug(f"Starting HTTP server... {self}")
        self.app = web.Application()
        self.app.add_routes(list(self.endpoints()))
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.site = web.TCPSite(runner, host=self.host, port=self.port)
        await self.site.start()

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
                if endpoint.interrupt:
                    func = _with_posthoc_task(func, self.raise_interrupt)
                yield endpoint.define(func)


def _with_posthoc_task(
    func: Callable[[web.Request], Awaitable[web.Response]],
    afterwards: Callable[[], Awaitable[None]],
) -> Callable[[web.Request], Awaitable[web.Response]]:
    # @functools.wraps
    async def wrapped(request: web.Request) -> web.Response:
        response = await func(request)
        await afterwards()
        return response

    return wrapped
