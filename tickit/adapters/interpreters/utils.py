from typing import AnyStr, AsyncIterable, List


async def wrap_as_async_iterable(message: AnyStr) -> AsyncIterable[AnyStr]:
    """Wraps a message in an asynchronous iterable.

    Args:
        message (AnyStr): A singular message.

    Returns:
        AsyncIterable[AnyStr]: An asynchronous iterable containing the message.
    """
    yield message


async def wrap_messages_as_async_iterable(
    messages: List[AnyStr],
) -> AsyncIterable[AnyStr]:
    """Wraps a message in an asynchronous iterable.

    Args:
        message (AnyStr): A singular message.

    Returns:
        AsyncIterable[AnyStr]: An asynchronous iterable containing the message.
    """
    for message in messages:
        yield message
