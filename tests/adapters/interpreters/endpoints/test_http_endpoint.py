import pytest
from aiohttp import web

from tickit.adapters.interpreters.endpoints.http_endpoint import HttpEndpoint


@pytest.fixture
def http_endpoint(url: str, method: str, interrupt: bool):
    return HttpEndpoint(url, method, interrupt)


def test_http_endpoint_registers_get_endpoint():
    class TestAdapter:
        @HttpEndpoint.get("test", False)
        def test_endpoint():
            pass

    assert isinstance(TestAdapter.test_endpoint.__endpoint__, HttpEndpoint)


def test_http_endpoint_registers_put_endpoint():
    class TestAdapter:
        @HttpEndpoint.put("test", False)
        def test_endpoint():
            pass

    assert isinstance(TestAdapter.test_endpoint.__endpoint__, HttpEndpoint)


def fake_endpoint(request: web.Request):
    pass


@pytest.mark.parametrize(
    ["url", "method", "interrupt", "expected"],
    [
        (
            r"TestUrl",
            r"GET",
            False,
            web.RouteDef("GET", "TestUrl", fake_endpoint, {}),
        )
    ],
)
def test_http_get_endpoint_define_returns_get_routedef(
    http_endpoint: HttpEndpoint, expected: web.RouteDef
):
    assert expected == http_endpoint.define(fake_endpoint)


@pytest.mark.parametrize(
    ["url", "method", "interrupt", "expected"],
    [
        (
            r"TestUrl",
            r"PUT",
            False,
            web.RouteDef("PUT", "TestUrl", fake_endpoint, {}),
        )
    ],
)
def test_http_put_endpoint_define_returns_put_routedef(
    http_endpoint: HttpEndpoint, expected: web.RouteDef
):
    assert expected == http_endpoint.define(fake_endpoint)
