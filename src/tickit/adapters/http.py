from collections.abc import Callable, Iterable
from inspect import getmembers

from tickit.adapters.specifications import HttpEndpoint
from tickit.core.adapter import RaiseInterrupt


class HttpAdapter:
    """An adapter interface for the HttpIo."""

    interrupt: RaiseInterrupt

    def get_endpoints(self) -> Iterable[tuple[HttpEndpoint, Callable]]:
        """Returns list of endpoints.

        Fetches the defined HTTP endpoints in the device adapter, parses them and
        then yields them.

        Returns:
            Iterable[HttpEndpoint]: The list of defined endpoints

        Yields:
            Iterator[Iterable[HttpEndpoint]]: The iterator of the defined endpoints
        """
        for _, func in getmembers(self):
            endpoint = getattr(func, "__endpoint__", None)  # type: ignore
            if endpoint is not None and isinstance(endpoint, HttpEndpoint):
                yield endpoint, func

    def after_update(self) -> None: ...
