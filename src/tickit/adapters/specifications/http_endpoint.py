from dataclasses import dataclass
from typing import AnyStr, Awaitable, Callable, Generic, Optional

from aiohttp import web
from aiohttp.web_response import StreamResponse
from aiohttp.web_routedef import RouteDef


@dataclass(frozen=True)
class HttpEndpoint(Generic[AnyStr]):
    """A decorator intended for use with HttpAdapter.

    Routes an HTTP endpoint to the decorated method.

    Args:
        path: The URL that will point to a specific endpoint.
        method: The method to use when using this endpoint.
        interrupt: If True, every time this endpoint is called the adapter's device
            will be interrupted. Defaults to False.

    Returns:
        Callable:
            A decorator which registers the adapter method as an endpoint.
    """

    path: str
    method: str
    interrupt: bool = False
    func: Optional[Callable[[web.Request], web.Response]] = None

    def __call__(self, func: Callable) -> Callable:
        """Decorate a function for HTTP routing.

        Args:
            func: The adapter method to be registered as an endpoint.

        Returns:
            Callable: The registered adapter endpoint.
        """
        setattr(func, "__endpoint__", self)
        return func

    def define(
        self, func: Callable[[web.Request], Awaitable[StreamResponse]]
    ) -> RouteDef:
        """Performs the construction of the endpoint RouteDef for the HTTP Server.

        A method which performs the construction of the route definition of the method,
         URL and handler function for the endpoint, to then return to the HTTP Server.

        Args:
            func (Callable): The handler function to be attached to the route
            definition for the endpoint.

        Returns:
            RouteDef: The route definition for the endpoint.
        """
        return RouteDef(self.method, self.path, func, {})

    @classmethod
    def get(cls, url: str, interrupt: bool = False) -> "HttpEndpoint":
        """Shortcut to making a GET endpoint.

        Returns:
            cls: The class of HttpEndpoint with the "GET" request method.
        """
        return cls(url, "GET", interrupt)

    @classmethod
    def put(cls, url: str, interrupt: bool = False) -> "HttpEndpoint":
        """Shortcut to making a PUT endpoint.

        Returns:
            cls: The class of HttpEndpoint with the "PUT" request method.
        """
        return cls(url, "PUT", interrupt)

    @classmethod
    def post(cls, url: str, interrupt: bool = False) -> "HttpEndpoint":
        """Shortcut to making a POST endpoint.

        Returns:
            cls: The class of HttpEndpoint with the "POST" request method.
        """
        return cls(url, "POST", interrupt)
