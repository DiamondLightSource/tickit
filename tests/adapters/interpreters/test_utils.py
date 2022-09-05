import pytest

from tickit.adapters.interpreters.utils import (
    wrap_as_async_iterable,
    wrap_messages_as_async_iterable,
)


@pytest.mark.asyncio
async def test_wrap_list_correctly():
    messages = ["Hello", "World"]
    wrapped = wrap_messages_as_async_iterable(messages)
    assert "Hello" == await anext(wrapped)  # noqa: F821
    assert "World" == await anext(wrapped)  # noqa: F821
    with pytest.raises(StopAsyncIteration):
        await anext(wrapped)  # noqa: F821


@pytest.mark.asyncio
async def test_wrap_message_correctly():
    message = b"Hello World"
    wrapped = wrap_as_async_iterable(message)
    assert b"Hello World" == await anext(wrapped)  # noqa: F821
    with pytest.raises(StopAsyncIteration):
        await anext(wrapped)  # noqa: F821
