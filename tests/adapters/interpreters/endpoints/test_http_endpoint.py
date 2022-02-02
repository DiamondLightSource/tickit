import pytest
from aiohttp import web

from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint


@pytest.fixture
def http_endpoint(url: str, method: str, include_json: bool, interrupt: bool):
    return HTTPEndpoint(url, method, include_json, interrupt)


def test_http_endpoint_registers_get_endpoint():
    class TestAdapter:
        @HTTPEndpoint.get("test", False, False)
        def test_endpoint():
            pass

    assert isinstance(TestAdapter.test_endpoint.__endpoint__, HTTPEndpoint)


def test_http_endpoint_registers_put_endpoint():
    class TestAdapter:
        @HTTPEndpoint.put("test", False, False)
        def test_endpoint():
            pass

    assert isinstance(TestAdapter.test_endpoint.__endpoint__, HTTPEndpoint)


def fake_endpoint(request: web.Request):
    pass


@pytest.mark.parametrize(
    ["url", "method", "include_json", "interrupt", "expected"],
    [
        (
            r"TestUrl",
            r"GET",
            False,
            False,
            web.RouteDef("GET", "TestUrl", fake_endpoint, {}),
        )
    ],
)
def test_http_get_endpoint_define_returns_get_routedef(
    http_endpoint: HTTPEndpoint, expected: web.RouteDef
):
    assert expected == http_endpoint.define(fake_endpoint)


@pytest.mark.parametrize(
    ["url", "method", "include_json", "interrupt", "expected"],
    [
        (
            r"TestUrl",
            r"PUT",
            False,
            False,
            web.RouteDef("PUT", "TestUrl", fake_endpoint, {}),
        )
    ],
)
def test_http_put_endpoint_define_returns_put_routedef(
    http_endpoint: HTTPEndpoint, expected: web.RouteDef
):
    assert expected == http_endpoint.define(fake_endpoint)
