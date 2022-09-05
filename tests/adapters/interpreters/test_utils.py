import pytest

from tickit.adapters.interpreters.utils import (
    wrap_as_async_iterable,
    wrap_messages_as_async_iterable,
)


@pytest.mark.asyncio
async def test_wrap_list_correctly():
    messages = ["Hello", "World"]
    wrapped = wrap_messages_as_async_iterable(messages)
    assert "Hello" == await wrapped.__anext__()
    assert "World" == await wrapped.__anext__()
    with pytest.raises(StopAsyncIteration):
        await wrapped.__anext__()


@pytest.mark.asyncio
async def test_wrap_message_correctly():
    message = b"Hello World"
    wrapped = wrap_as_async_iterable(message)
    assert b"Hello World" == await wrapped.__anext__()
    with pytest.raises(StopAsyncIteration):
        await wrapped.__anext__()
