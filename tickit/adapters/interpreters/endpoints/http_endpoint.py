from dataclasses import dataclass
from typing import AnyStr, Awaitable, Callable, Generic, Optional, Sequence

from aiohttp.web import Request, get, put
from aiohttp.web_routedef import RouteDef


@dataclass(frozen=True)
class HTTPEndpoint(Generic[AnyStr]):
    """A decorator to register an adapter method as a HTTP Endpoint.

    Args:
        route (str): The URL that will point to a specific endpoint.
        interrupt (bool): A flag indicating whether calling of the method should
            raise an adapter interrupt. Defaults to False.
        format (Optional[str]): The message decoding format to be used for string
            based interpretation. Defaults to None.

    Returns:
        Callable:
            A decorator which registers the adapter method as a message handler.
    """

    url: str
    method: str
    name: str
    include_json: bool = False
    interrupt: bool = False

    def __call__(self, func: Callable) -> Callable:
        """A decorator which registers the adapter method as a message handler.

        Args:
            func (Callable): The adapter method to be registered as a command.

        Returns:
            Callable: The registered adapter method.
        """
        setattr(func, "__endpoint__", self)
        return func

    def parse(self, func: Callable) -> RouteDef:
        """Performs the parsing of the URL and extracts any info if it's a get request.

        A method which performs pasing of the URL to extract, otherwise the method
        returns None.

        Args:
            url (str): The URL to be parsed.

        Returns:
            Optional[AnyStr]:
                If any data is passed to the endpoint, a str is returned,
                otherwise the method returns None.
        """
        return RouteDef(self.method, self.url, func, {})
