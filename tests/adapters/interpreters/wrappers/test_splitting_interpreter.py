from typing import AnyStr, AsyncIterable, List, Tuple

import pytest
from mock import ANY, AsyncMock, patch

from tickit.adapters.interpreters.utils import wrap_as_async_iterable
from tickit.adapters.interpreters.wrappers import SplittingInterpreter
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
