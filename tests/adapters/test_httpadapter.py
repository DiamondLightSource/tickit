from typing import Iterable

import pytest
from aiohttp import web
from mock import Mock
from mock.mock import create_autospec, patch

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
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


class MockAdapter(HTTPAdapter):
    device: Device

    @HTTPEndpoint.get("/mock_endpoint")
    async def mock_endpoint(self, request: web.Request) -> web.Response:
        return web.Response(text="test")


@pytest.fixture
def http_adapter() -> HTTPAdapter:
    http_adapter = HTTPAdapter()
    return http_adapter


@pytest.mark.skip(ISSUE_LINK)
def test_http_adapter_constructor():
    HTTPAdapter()


@pytest.fixture
def patch_asyncio_event_wait() -> Iterable[Mock]:
    with patch(
        "tickit.core.components.device_simulation.asyncio.Event.wait", autospec=True
    ) as mock:
        yield mock


@pytest.mark.asyncio
@pytest.mark.skip(ISSUE_LINK)
async def test_http_adapter_run_forever_method(
    http_adapter: HTTPAdapter,
    mock_device: Device,
    mock_raise_interrupt: Mock,
    patch_asyncio_event_wait: Mock,
):
    await http_adapter.run_forever(mock_device, mock_raise_interrupt)
    await http_adapter.shutdown()

    patch_asyncio_event_wait.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.skip(ISSUE_LINK)
async def test_http_adapter_endpoints():
    adapter = MockAdapter()

    resp = await list(adapter.endpoints())[0].handler(None)

    assert resp.text == "test"
