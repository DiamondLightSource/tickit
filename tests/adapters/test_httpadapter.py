import asyncio
from typing import Iterable
import aiohttp

import pytest
import pytest_asyncio
import requests
from aiohttp import web
from mock import Mock
from mock.mock import create_autospec, patch

from tickit.adapters.httpadapter import HttpAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HttpEndpoint
from tickit.core.device import Device

ISSUE_LINK = "https://github.com/dls-controls/tickit/issues/111"


@pytest.fixture
def mock_device() -> Device:
    return create_autospec(Device)


@pytest.fixture
def mock_raise_interrupt():
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


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

    @HttpEndpoint.get("/bar/{name}")
    async def get_bar(self, request: web.Request) -> web.Response:
        name = request.match_info["name"]
        return web.json_response({"entity": name, "value": "bar"})

    @HttpEndpoint.put("/bar/{name}")
    async def put_bar(self, request: web.Request) -> web.Response:
        name = request.match_info["name"]
        value = (await request.json())["value"]
        return web.json_response({"entity": name, "value": value})

    @HttpEndpoint.post("/bar/{name}")
    async def post_bar(self, request: web.Request) -> web.Response:
        name = request.match_info["name"]
        value = (await request.json())["value"]
        return web.json_response({"entity": name, "value": value})

    @HttpEndpoint.get("/baz")
    async def get_baz(self, request: web.Request) -> web.Response:
        return web.Response(status=403)


@pytest.fixture
def adapter() -> HttpAdapter:
    http_adapter = ExampleAdapter()
    return http_adapter


@pytest_asyncio.fixture
async def adapter_url(
    adapter: HttpAdapter, mock_device: Device, event_loop: asyncio.BaseEventLoop
):
    task = event_loop.create_task(adapter.run_forever(mock_device, lambda: None))
    await adapter.wait_until_ready(timeout=10.0)
    yield f"http://localhost:{adapter.port}"
    await adapter.stop()
    await asyncio.wait_for(task, timeout=10.0)


@pytest.mark.asyncio
async def test_http_adapter_get(adapter_url: str):
    url = f"{adapter_url}/foo"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            assert response.status == 200
            assert (await response.json()) == {"value": "foo"}


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["a", "b"])
async def test_http_adapter_get_by_name(adapter_url: str, name: str):
    url = f"{adapter_url}/bar/{name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            assert response.status == 200
            assert (await response.json()) == {"entity": name, "value": "bar"}


@pytest.mark.asyncio
async def test_http_adapter_error_code(adapter_url: str):
    url = f"{adapter_url}/baz"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            assert response.status == 403


@pytest.mark.asyncio
async def test_http_adapter_put(adapter_url: str):
    url = f"{adapter_url}/foo"
    async with aiohttp.ClientSession() as session:
        async with session.put(url, json={"value": "bar"}) as response:
            assert response.status == 200
            assert (await response.json()) == {"value": "bar"}


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["a", "b"])
async def test_http_adapter_put_by_name(adapter_url: str, name: str):
    url = f"{adapter_url}/bar/{name}"
    async with aiohttp.ClientSession() as session:
        async with session.put(url, json={"value": "foo"}) as response:
            assert response.status == 200
            assert (await response.json()) == {"entity": name, "value": "foo"}


@pytest.mark.asyncio
async def test_http_adapter_post(adapter_url: str):
    url = f"{adapter_url}/foo"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"value": "bar"}) as response:
            assert response.status == 200
            assert (await response.json()) == {"value": "bar"}


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["a", "b"])
async def test_http_adapter_post_by_name(adapter_url: str, name: str):
    url = f"{adapter_url}/bar/{name}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"value": "foo"}) as response:
            assert response.status == 200
            assert (await response.json()) == {"entity": name, "value": "foo"}
