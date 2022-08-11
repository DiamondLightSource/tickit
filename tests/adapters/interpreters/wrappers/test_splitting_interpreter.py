import asyncio
import time
from typing import AnyStr, AsyncIterable, List, Tuple, Type, Union

import pytest
from mock import ANY, AsyncMock, patch

from tickit.adapters.interpreters.utils import wrap_as_async_iterable
from tickit.adapters.interpreters.wrappers import (
    AsyncSplittingInterpreter,
    SplittingInterpreter,
    SyncSplittingInterpreter,
)
from tickit.core.adapter import Adapter


async def dummy_response(msg: AnyStr) -> Tuple[AsyncIterable[AnyStr], bool]:
    return wrap_as_async_iterable(msg), True


class DummySplittingInterpreter(SplittingInterpreter):
    """SplittingInterpreter with dummy implementation of abstract method."""

    async def _handle_individual_messages(
        self, adapter: Adapter, individual_messages: List[AnyStr]
    ) -> List[Tuple[AsyncIterable[AnyStr], bool]]:
        return [await dummy_response(msg) for msg in individual_messages]


async def _test_sub_messages(
    splitting_interpreter: DummySplittingInterpreter,
    mock_handle_individual_messages: AsyncMock,
    mock_get_response: AsyncMock,
    test_message: AnyStr,
    expected_sub_messages: List[AnyStr],
):
    mock_get_response.return_value = await dummy_response(test_message)
    await splitting_interpreter.handle(AsyncMock(), test_message)
    mock_handle_individual_messages.assert_called_once_with(ANY, expected_sub_messages)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_message, delimiter, expected_sub_messages",
    [
        ("test message", " ", ["test", "message"]),
        (b"foo/bar", b"/", [b"foo", b"bar"]),
        ("single message", "/", ["single message"]),
    ],
)
@patch.object(
    DummySplittingInterpreter, "_get_response_and_interrupt_from_individual_results"
)
@patch.object(DummySplittingInterpreter, "_handle_individual_messages")
async def test_handle_passes_on_correct_sub_messages(
    mock_handle_individual_messages: AsyncMock,
    mock_get_response: AsyncMock,
    test_message: AnyStr,
    delimiter: AnyStr,
    expected_sub_messages: List[AnyStr],
):
    splitting_interpreter = DummySplittingInterpreter(AsyncMock(), delimiter)

    await _test_sub_messages(
        splitting_interpreter,
        mock_handle_individual_messages,
        mock_get_response,
        test_message,
        expected_sub_messages,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_message, expected_sub_messages",
    [
        (b"test message", [b"test", b"message"]),
        (b"foo/bar", [b"foo/bar"]),
    ],
)
@patch.object(
    DummySplittingInterpreter, "_get_response_and_interrupt_from_individual_results"
)
@patch.object(DummySplittingInterpreter, "_handle_individual_messages")
async def test_handle_passes_on_correct_sub_messages_with_default_delimiter(
    mock_handle_individual_messages: AsyncMock,
    mock_get_response: AsyncMock,
    test_message: AnyStr,
    expected_sub_messages: List[AnyStr],
):
    splitting_interpreter = DummySplittingInterpreter(AsyncMock())

    await _test_sub_messages(
        splitting_interpreter,
        mock_handle_individual_messages,
        mock_get_response,
        test_message,
        expected_sub_messages,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    [
        "individual_messages",
        "individual_interrupts",
        "expected_combined_message",
        "expected_combined_interrupt",
    ],
    [
        (["one", "two"], [False, False], "onetwo", False),
        (["three", "four"], [False, True], "threefour", True),
        (["five", "six"], [True, True], "fivesix", True),
    ],
)
@patch(
    "tickit.adapters.interpreters.wrappers.splitting_interpreter.wrap_as_async_iterable"
)
async def test_individual_results_combined_correctly(
    mock_wrap_message: AsyncMock,
    individual_messages: List[AnyStr],
    individual_interrupts: List[bool],
    expected_combined_message: AnyStr,
    expected_combined_interrupt: bool,
):
    splitting_interpreter = DummySplittingInterpreter(AsyncMock(), " ")
    individual_results = [
        (wrap_as_async_iterable(msg), interrupt)
        for msg, interrupt in zip(individual_messages, individual_interrupts)
    ]
    (
        _,
        combined_interrupt,
    ) = await splitting_interpreter._get_response_and_interrupt_from_individual_results(
        individual_results
    )
    mock_wrap_message.assert_called_once_with(expected_combined_message)
    assert combined_interrupt == expected_combined_interrupt


TEST_HANDLE_TIME = 0.1
NUM_HANDLE_CALLS = 3


async def dummy_slow_handle(*args):
    await asyncio.sleep(TEST_HANDLE_TIME)


async def time_handle_individual_messages(
    splitting_interpreter_type: Type[
        Union[SyncSplittingInterpreter, AsyncSplittingInterpreter]
    ],
) -> float:
    mock_interpreter = AsyncMock()
    mock_interpreter.handle = dummy_slow_handle
    splitting_interpreter = splitting_interpreter_type(mock_interpreter)
    t0 = time.time()
    await splitting_interpreter._handle_individual_messages(
        AsyncMock(), ["one", "two", "three"]
    )
    t1 = time.time()
    return t1 - t0


@pytest.mark.asyncio
async def test_async_splitting_interpreter_handles_messages_asynchronously():
    total_handle_time = await time_handle_individual_messages(AsyncSplittingInterpreter)
    assert total_handle_time < NUM_HANDLE_CALLS * TEST_HANDLE_TIME


@pytest.mark.asyncio
async def test_sync_splitting_interpreter_handles_messages_synchronously():
    total_handle_time = await time_handle_individual_messages(SyncSplittingInterpreter)
    assert total_handle_time > NUM_HANDLE_CALLS * TEST_HANDLE_TIME
