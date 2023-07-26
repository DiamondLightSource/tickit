from abc import ABC, abstractmethod
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    Optional,
    Tuple,
    TypeVar,
)

from tickit.core.adapter import RaiseInterrupt

#: Message type
T = TypeVar("T")


class RawTcpIo(AdapterIo):
    async def setup(self, adapter: object) -> None:
        commands = collect_commands(adapter)
        await start_tcp_server(commands)


A = TypeVar("A")
I = TypeVar("I")


class AdapterIo(ABC, Generic[A]):
    """Demand adapter io objects have a setup method for an adapter object."""

    @abstractmethod
    async def setup(self, adapter: A) -> None:
        ...


class AdapterContainer(Generic[A]):
    """This Is a container for an object specific interface and the required functional io."""

    adapter: A
    io: AdapterIo

    async def run_forever(self, raise_interrupt: RaiseInterrupt) -> None:
        """An asynchronous method allowing indefinite running of core adapter logic.

        An asynchronous method allowing for indefinite running of core adapter logic
        (typically the hosting of a protocol server and the interpretation of commands
        which are supplied via it).
        """

        await self.io.setup(self.adapter, raise_interrupt)


class HttpIo:
    async def setup(
        self,
        adapter: object,
        raise_interrupt: RaiseInterrupt,
    ) -> None:
        endpoints = adapter.get_endpoints()
        for endpoint in self.get_endpoints(adapter):
            if endpoint.interrupt:
                endpoint.add_post_task(raise_interrupt)
        await start_sever(endpoints)

    def get_endpoints(self, adapter: object) -> Iterable[HttpEndpoint]:
        for field in adapter.__dict__.items():
            if isinstance(field, HttpEndpoint):
                yield field


from tickit.adapters.interpreters.endpoints.http_endpoint import HttpEndpoint


class Eiger:
    ...


class EigerAdapter(HttpAdapter):
    eiger: Eiger

    def __init__(self, eiger: Eiger) -> None:
        super().__init__()
        self.eiger = eiger

    @HttpEndpoint.get("/foo")
    async def get_foo(self, request):
        foo = eiger.foo
        return {"foo": foo}

    @HttpEndpoint.put("/foo", interrupt=True)
    async def put_foo(self, request):
        old_foo = self.get_foo()["foo"]
        eiger.foo = request.foo
        new_foo = self.get_foo()["foo"]
        return {"old_foo": old_foo, "new_foo": new_foo}
