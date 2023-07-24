from collections.abc import AsyncIterator
from typing import AnyStr, Iterable


async def wrap_as_async_iterator(message: AnyStr) -> AsyncIterator[AnyStr]:
    """Wraps a message in an asynchronous iterator.

    Args:
        message (AnyStr): A singular message.

    Returns:
        AsyncIterator[AnyStr]: An asynchronous iterator containing the message.
    """
    yield message


async def wrap_messages_as_async_iterator(
    messages: Iterable[AnyStr],
) -> AsyncIterator[AnyStr]:
    """Wraps a message in an asynchronous iterator.

    Args:
        message (AnyStr): An iterable containing a number of messages.

    Returns:
        AsyncIterator[AnyStr]: An asynchronous iterator containing the messages.
    """
    for message in messages:
        yield message
