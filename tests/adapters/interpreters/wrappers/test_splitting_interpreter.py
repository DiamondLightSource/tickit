from typing import AnyStr, AsyncIterable, List, Tuple

import pytest
from mock import ANY, AsyncMock, call, patch

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
    "test_message, message_delimiter, expected_sub_messages",
    [
        ("test message", " ", ["test", "message"]),
        (b"foo/bar", b"/", [b"foo", b"bar"]),
        ("single message", "/", ["single message"]),
        ("just1the2words", r"[1-4]", ["just", "the", "words"]),
        ("#1J=1 #2 P", r"(#[1-8])|\s", ["", "#1", "J=1", "", "#2", "", "P"]),
    ],
)
@patch.object(DummySplittingInterpreter, "_collect_responses")
@patch.object(DummySplittingInterpreter, "_handle_individual_messages")
async def test_handle_passes_on_correct_sub_messages(
    mock_handle_individual_messages: AsyncMock,
    mock_get_response: AsyncMock,
    test_message: AnyStr,
    message_delimiter: AnyStr,
    expected_sub_messages: List[AnyStr],
):
    splitting_interpreter = DummySplittingInterpreter(
        AsyncMock(),
        message_delimiter,
    )

    await _test_sub_messages(
        splitting_interpreter,
        mock_handle_individual_messages,
        mock_get_response,
        test_message,
        expected_sub_messages,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("sub_messages", [["one", "two", "three"], ["test", "message"]])
async def test_handle_individual_messages_makes_correct_handle_calls(sub_messages):
    mock_interpreter = AsyncMock()
    splitting_interpreter = SplittingInterpreter(mock_interpreter, " ")
    await splitting_interpreter._handle_individual_messages(AsyncMock(), sub_messages)
    mock_handle_calls = mock_interpreter.handle.mock_calls
    assert mock_handle_calls == [call(ANY, msg) for msg in sub_messages]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    [
        "individual_messages",
        "individual_interrupts",
        "expected_combined_interrupt",
    ],
    [
        (["one", "two"], [False, False], False),
        (["three", "four"], [False, True], True),
        (["five", "six"], [True, True], True),
    ],
)
@patch(
    "tickit.adapters.interpreters.wrappers."
    "splitting_interpreter.wrap_messages_as_async_iterable"
)
async def test_individual_results_combined_correctly(
    mock_wrap_message: AsyncMock,
    individual_messages: List[AnyStr],
    individual_interrupts: List[bool],
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
    ) = await splitting_interpreter._collect_responses(individual_results)
    mock_wrap_message.assert_called_once_with(individual_messages)
    assert combined_interrupt == expected_combined_interrupt


@pytest.mark.asyncio
@patch(
    "tickit.adapters.interpreters.wrappers."
    "splitting_interpreter.wrap_messages_as_async_iterable"
)
async def test_multi_resp(
    mock_wrap_message: AsyncMock,
):
    async def multi_resp(msgs):
        for msg in msgs:
            yield msg

    splitting_interpreter = DummySplittingInterpreter(AsyncMock(), " ")
    individual_results = [(multi_resp(["resp1", "resp2"]), True)]
    await splitting_interpreter._collect_responses(individual_results)
    mock_wrap_message.assert_called_once_with(["resp1", "resp2"])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["message_delimiter", "response_delimiter"], [(" ", "/"), ("/", " ")]
)
@patch.object(DummySplittingInterpreter, "_collect_responses")
@patch.object(DummySplittingInterpreter, "_handle_individual_messages")
async def test_handles_empty_messages_correctly(
    mock_handle_individual_messages: AsyncMock,
    mock_collect: AsyncMock,
    message_delimiter: str,
    response_delimiter: str,
):
    splitting_interpreter = DummySplittingInterpreter(AsyncMock(), message_delimiter)
    mock_collect.return_value = "", False

    await splitting_interpreter.handle(AsyncMock(), "")

    mock_handle_individual_messages.assert_called_once_with(ANY, [""])


@pytest.mark.parametrize(
    ["message", "message_delimiter"], [(" ", " "), (" ", r"\s"), ("delim", "delim")]
)
@patch.object(DummySplittingInterpreter, "_collect_responses")
@patch.object(DummySplittingInterpreter, "_handle_individual_messages")
@pytest.mark.asyncio
async def test_delimiter_only_message_results_in_empty_messages_handled(
    mock_handle_individual_messages: AsyncMock,
    mock_collect: AsyncMock,
    message: str,
    message_delimiter: str,
):
    splitting_interpreter = DummySplittingInterpreter(
        AsyncMock(),
        message_delimiter,
    )
    mock_collect.return_value = "", False

    await splitting_interpreter.handle(AsyncMock(), message)

    mock_handle_individual_messages.assert_called_once_with(ANY, ["", ""])
