from typing import Callable

import pytest
from aiohttp import web

from tickit.adapters.http import HttpAdapter
from tickit.adapters.specifications.http_endpoint import HttpEndpoint
from tickit.core.device import Device


class ExampleAdapter(HttpAdapter):
    device: Device

    @HttpEndpoint.get("/foo")
    async def get_foo(self, request: web.Request) -> web.Response:
        return web.json_response({"value": "foo"})

    @HttpEndpoint.put("/foo")
    async def put_foo(self, request: web.Request) -> web.Response:
        value = (await request.json())["value"]
        return web.json_response({"value": value})

    @HttpEndpoint.post("/foo")
    async def post_foo(self, request: web.Request) -> web.Response:
        value = (await request.json())["value"]
        return web.json_response({"value": value})

    def not_an_endpoint(self):
        pass


@pytest.fixture
def adapter() -> HttpAdapter:
    http_adapter = ExampleAdapter()
    return http_adapter


def test_adapter_has_three_endpoints(adapter: HttpAdapter):
    endpoints = adapter.get_endpoints()
    endpoints = list(endpoints)

    assert len(endpoints) == 3

    for endpoint in endpoints:
        assert isinstance(endpoint[0], HttpEndpoint)
        assert isinstance(endpoint[1], Callable)


def test_adapter_has_after_update_method(adapter: HttpAdapter):
    assert hasattr(adapter, "after_update")
    assert callable(adapter.after_update)


def test_adapter_after_update_method_returns_none(adapter: HttpAdapter):
    assert adapter.after_update() is None
