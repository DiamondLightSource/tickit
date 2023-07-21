import asyncio

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import web
from mock import Mock
from mock.mock import create_autospec

from tickit.adapters.httpadapter import HttpAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HttpEndpoint
from tickit.core.adapter import RaiseInterrupt
from tickit.core.device import Device

ISSUE_LINK = "https://github.com/dls-controls/tickit/issues/111"
REQUEST_TIMEOUT = 0.5


@pytest.fixture
def mock_device() -> Device:
    return create_autospec(Device)


@pytest.fixture
def mock_raise_interrupt() -> RaiseInterrupt:
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

    @HttpEndpoint.get("/error")
    async def cause_error(self, request: web.Request) -> web.Response:
        raise Exception("An error has occurred")

    @HttpEndpoint.put("/interrupt/{name}", interrupt=True)
    async def put_interrupt(self, request: web.Request) -> web.Response:
        name = request.match_info["name"]
        value = (await request.json())["value"]
        return web.json_response({"entity": name, "value": value})


@pytest.fixture
def adapter() -> HttpAdapter:
    http_adapter = ExampleAdapter()
    return http_adapter


@pytest_asyncio.fixture
async def adapter_task(
    adapter: HttpAdapter,
    mock_raise_interrupt: RaiseInterrupt,
    mock_device: Device,
    event_loop: asyncio.BaseEventLoop,
):
    adapter_running = event_loop.create_task(
        adapter.run_forever(mock_device, mock_raise_interrupt)
    )
    adapter_ready = event_loop.create_task(adapter.wait_until_ready())

    # either wait until the task has an exception or it's ready.
    done, _ = await asyncio.wait(
        [adapter_running, adapter_ready], return_when=asyncio.tasks.FIRST_COMPLETED
    )

    if adapter_running in done:
        exception = adapter_running.exception()
        if exception is not None:
            raise exception

    yield adapter_running
    await adapter.stop()
    await asyncio.wait_for(adapter_running, timeout=10.0)
    assert adapter_running.done()


@pytest_asyncio.fixture
async def adapter_url(adapter_task: asyncio.Task, adapter: HttpAdapter):
    yield f"http://localhost:{adapter.port}"


@pytest.mark.asyncio
async def test_shuts_down_server_on_cancel(
    adapter: HttpAdapter,
    adapter_task: asyncio.Task,
    adapter_url: str,
):
    # Verify server is up
    await assert_server_is_up(adapter_url)

    # Cancel task
    adapter_task.cancel()
    try:
        await adapter_task
    except asyncio.CancelledError:
        pass

    # Verify server is now down
    await assert_server_is_down(adapter_url)


@pytest.mark.asyncio
async def test_stop_is_idempotent(
    adapter: HttpAdapter,
    adapter_task: asyncio.Task,
    adapter_url: str,
    mock_raise_interrupt: RaiseInterrupt,
    mock_device: Device,
) -> None:
    # First ensure the server is working, then stop it and
    # ensure it is no longer working
    await assert_server_is_up(adapter_url)
    await adapter.stop()
    await adapter_task
    assert adapter_task.done()
    await assert_server_is_down(adapter_url)

    for i in range(2):
        # Then start it again and check it is working
        new_task = asyncio.create_task(
            adapter.run_forever(
                mock_device,
                mock_raise_interrupt,
            )
        )
        await adapter.wait_until_ready()
        await assert_server_is_up(adapter_url)

        # Finally stop it one more time and check it is stopped
        await adapter.stop()
        await new_task
        assert new_task.done()
        await assert_server_is_down(adapter_url)


async def assert_server_is_up(adapter_url: str) -> None:
    url = f"{adapter_url}/foo"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            assert response.status == 200


async def assert_server_is_down(adapter_url: str) -> None:
    url = f"{adapter_url}/foo"
    with pytest.raises(aiohttp.ClientConnectionError):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
                assert response.status == 200


@pytest.mark.asyncio
async def test_get(adapter_url: str):
    url = f"{adapter_url}/foo"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            assert response.status == 200
            assert (await response.json()) == {"value": "foo"}


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["a", "b"])
async def test_get_by_name(adapter_url: str, name: str):
    url = f"{adapter_url}/bar/{name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            assert response.status == 200
            assert (await response.json()) == {"entity": name, "value": "bar"}


@pytest.mark.asyncio
async def test_error_code(adapter_url: str):
    url = f"{adapter_url}/baz"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            assert response.status == 403


@pytest.mark.asyncio
async def test_internal_error(adapter_url: str):
    url = f"{adapter_url}/error"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            assert response.status == 500


@pytest.mark.asyncio
async def test_put(adapter_url: str):
    url = f"{adapter_url}/foo"
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url, json={"value": "bar"}, timeout=REQUEST_TIMEOUT
        ) as response:
            assert response.status == 200
            assert (await response.json()) == {"value": "bar"}


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["a", "b"])
async def test_put_by_name(adapter_url: str, name: str):
    url = f"{adapter_url}/bar/{name}"
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url, json={"value": "foo"}, timeout=REQUEST_TIMEOUT
        ) as response:
            assert response.status == 200
            assert (await response.json()) == {"entity": name, "value": "foo"}


@pytest.mark.asyncio
async def test_post(adapter_url: str):
    url = f"{adapter_url}/foo"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json={"value": "bar"}, timeout=REQUEST_TIMEOUT
        ) as response:
            assert response.status == 200
            assert (await response.json()) == {"value": "bar"}


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["a", "b"])
async def test_post_by_name(adapter_url: str, name: str):
    url = f"{adapter_url}/bar/{name}"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json={"value": "foo"}, timeout=REQUEST_TIMEOUT
        ) as response:
            assert response.status == 200
            assert (await response.json()) == {"entity": name, "value": "foo"}


@pytest.mark.asyncio
async def test_put_to_non_interrupting_endpoint_does_not_interrupt(
    mock_raise_interrupt: Mock,
    adapter_url: str,
):
    url = f"{adapter_url}/foo"
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url, json={"value": "bar"}, timeout=REQUEST_TIMEOUT
        ) as response:
            assert response.status == 200
            assert (await response.json()) == {"value": "bar"}
    mock_raise_interrupt.assert_not_called()


@pytest.mark.asyncio
async def test_put_to_interrupt(
    mock_raise_interrupt: Mock,
    adapter_url: str,
):
    url = f"{adapter_url}/interrupt/a"
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url, json={"value": "foo"}, timeout=REQUEST_TIMEOUT
        ) as response:
            assert response.status == 200
            assert (await response.json()) == {"entity": "a", "value": "foo"}
    mock_raise_interrupt.assert_called_once()
