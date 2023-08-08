import asyncio
import logging
from typing import Awaitable, Callable, Iterable, Optional, Tuple

from aiohttp import web
from aiohttp.web_routedef import RouteDef

from tickit.adapters.http import HttpAdapter
from tickit.adapters.specifications import HttpEndpoint
from tickit.core.adapter import AdapterIo, RaiseInterrupt

LOGGER = logging.getLogger(__name__)


class HttpIo(AdapterIo[HttpAdapter]):
    """An AdapterIo implementation which delegates to a server and sets up endpoints.

    An AdapterIo implementation which delegates the hosting of an http requests to a
    server and sets up the endpoints for said server from a HttpAdapter.
    """

    host: str
    port: int

    _stopped: Optional[asyncio.Event]
    _ready: Optional[asyncio.Event]

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
    ) -> None:
        self.host = host
        self.port = port
        self._stopped = None
        self._ready = None

    async def setup(
        self, adapter: HttpAdapter, raise_interrupt: RaiseInterrupt
    ) -> None:
        adapter.interrupt = raise_interrupt
        self._ensure_stopped_event().clear()
        endpoints = adapter.get_endpoints()
        await self._start_server(endpoints, raise_interrupt)
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

    async def _start_server(
        self,
        endpoints: Iterable[Tuple[HttpEndpoint, Callable]],
        raise_interrupt: RaiseInterrupt,
    ):
        LOGGER.debug(f"Starting HTTP server... {self}")
        self.app = web.Application()
        definitions = self.create_route_definitions(endpoints, raise_interrupt)
        self.app.add_routes(list(definitions))
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.site = web.TCPSite(runner, host=self.host, port=self.port)
        await self.site.start()

    def create_route_definitions(
        self,
        endpoints: Iterable[Tuple[HttpEndpoint, Callable]],
        raise_interrupt: RaiseInterrupt,
    ) -> Iterable[RouteDef]:
        for endpoint, func in endpoints:
            if endpoint.interrupt:
                func = _with_posthoc_task(func, raise_interrupt)
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
