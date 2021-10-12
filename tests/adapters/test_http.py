import pytest
from aiohttp import web
from mock import Mock, PropertyMock, create_autospec

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.servers.http_server import HTTPServer
from tickit.core.device import Device


@pytest.fixture
def MockDevice() -> Mock:
    return create_autospec(Device, instance=False)


@pytest.fixture
def mock_device() -> Mock:
    return create_autospec(Device, instance=True)


@pytest.fixture
def MockServer() -> Mock:
    return create_autospec(HTTPServer, instance=False)


@pytest.fixture
def mock_server() -> Mock:
    return create_autospec(HTTPServer, instance=True)


@pytest.fixture
def MockServerConfig() -> Mock:
    return create_autospec(HTTPServer.HTTPServerConfig, instance=False)


@pytest.fixture
def mock_server_config() -> Mock:
    return create_autospec(HTTPServer.HTTPServerConfig, instance=True)


@pytest.fixture
def populated_mock_server_config(mock_server_config: Mock, MockServer: Mock) -> Mock:
    mock_server_config.configures.return_value = MockServer
    type(mock_server_config).kwargs = PropertyMock(
        return_value={"host": "localhost", "port": 8080, "format": b"%b\r\n"}
    )
    return mock_server_config


@pytest.fixture
def raise_interrupt():
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def http_adapter(
    mock_device: Mock, raise_interrupt: Mock, mock_server: Mock,
):
    return type("TestHTTPAdapter", (HTTPAdapter,), {})(
        mock_device, raise_interrupt, mock_server,
    )


@pytest.mark.asyncio
async def test_http_adapter_run_forever_runs_server(http_adapter: Mock):
    http_adapter._server.app = web.Application()
    http_adapter._server.routes = web.RouteTableDef()
    await http_adapter.run_forever()
    http_adapter._server.run_forever.assert_called_once_with()
