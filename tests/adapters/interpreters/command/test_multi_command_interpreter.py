from typing import AsyncIterable

import pytest
from mock import AsyncMock, MagicMock, patch

from tickit.adapters.interpreters.command import MultiCommandInterpreter
from tickit.adapters.interpreters.command.command_interpreter import Command

_GET_TYPE_HINTS = (
    "tickit.adapters.interpreters.command.multi_command_interpreter.get_type_hints"
)


@pytest.fixture
def multi_command_interpreter():
    return MultiCommandInterpreter()


def test_get_longest_match_returns_correct_longest_match_info(
    multi_command_interpreter: MultiCommandInterpreter,
):
    test_methods = [
        AsyncMock(
            __command__=MagicMock(
                Command,
                parse=MagicMock(return_value=((f"arg{i}"), i, 2, 2)),
            ),
        )
        for i in range(3)
    ]
    test_match_info = multi_command_interpreter._get_longest_match_info(
        "Test message", [method.__command__ for method in test_methods], test_methods
    )
    assert test_match_info is not None
    assert test_match_info.command_args == "arg0"


def test_get_longest_match_info_returns_none_if_no_match(
    multi_command_interpreter: MultiCommandInterpreter,
):
    test_method = AsyncMock(
        __command__=MagicMock(
            Command,
            parse=MagicMock(return_value=None),
        ),
    )
    test_match_info = multi_command_interpreter._get_longest_match_info(
        "Test message", [test_method.__command__], [test_method]
    )
    assert test_match_info is None


def test_get_longest_match_info_returns_none_if_match_not_at_start(
    multi_command_interpreter: MultiCommandInterpreter,
):
    test_method = AsyncMock(
        __command__=MagicMock(
            Command,
            parse=MagicMock(return_value=(("arg"), 1, 2, 2)),
        ),
    )
    test_match_info = multi_command_interpreter._get_longest_match_info(
        "Test message", [test_method.__command__], [test_method]
    )
    assert test_match_info is None


def test_get_longest_match_returns_none_if_no_command(
    multi_command_interpreter: MultiCommandInterpreter,
):
    test_match_info = multi_command_interpreter._get_longest_match_info(
        "Test message", [None], [AsyncMock()]
    )
    assert test_match_info is None


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": int, "arg2": float},
)
@pytest.mark.asyncio
async def test_execute_command_from_match_info_correctly(
    multi_command_interpreter: MultiCommandInterpreter,
):
    test_method = AsyncMock(
        __command__=MagicMock(Command),
    )
    test_match_info = MagicMock(command_method=test_method, command_args=("1", "2"))
    await multi_command_interpreter._execute_command_from_match(test_match_info)
    test_method.assert_awaited_once_with(int(1), float(2))


@pytest.mark.parametrize(
    "message, match_length, ignore_whitespace, expected",
    [("Test message", 4, False, " message"), ("Test message", 4, True, "message")],
)
def test_get_remaining_message_trims_correctly(
    multi_command_interpreter: MultiCommandInterpreter,
    message,
    match_length,
    ignore_whitespace,
    expected,
):
    multi_command_interpreter = MultiCommandInterpreter(
        ignore_whitespace=ignore_whitespace
    )
    test_match_info = MagicMock(match_length=match_length)
    trimmed_message = multi_command_interpreter._get_remaining_message(
        message, test_match_info
    )
    assert trimmed_message == expected


@pytest.mark.asyncio
@patch.object(
    MultiCommandInterpreter,
    "_get_longest_match_info",
    MagicMock(return_value=None),
)
async def test_execute_commands_returns_none_if_no_match(
    multi_command_interpreter: MultiCommandInterpreter,
):
    result = await multi_command_interpreter._execute_commands_in_message(
        "test", MagicMock()
    )
    assert result is None


@pytest.mark.asyncio
@patch.object(
    MultiCommandInterpreter,
    "_get_longest_match_info",
    MagicMock(),
)
@patch.object(
    MultiCommandInterpreter,
    "_get_remaining_message",
    MagicMock(side_effect=[True, False]),
)
async def test_execute_commands_in_message_combines_responses_correctly(
    multi_command_interpreter: MultiCommandInterpreter,
):
    async def multi_response() -> AsyncIterable[str]:
        yield "response1"
        yield "response2"

    with patch.object(
        MultiCommandInterpreter,
        "_execute_command_from_match",
        AsyncMock(side_effect=[(multi_response(), False), ("response3", True)]),
    ):
        result = await multi_command_interpreter._execute_commands_in_message(
            "test", MagicMock()
        )
    assert result is not None
    responses, interrupts = result
    assert responses == ["response1", "response2", "response3"]
    assert interrupts == [False, True]


@pytest.mark.asyncio
@patch.object(
    MultiCommandInterpreter,
    "_execute_commands_in_message",
    AsyncMock(return_value=None),
)
async def test_handle_calls_unknown_command_if_no_match(
    multi_command_interpreter: MultiCommandInterpreter,
):
    resp, interrupt = await multi_command_interpreter.handle(AsyncMock(), "test")
    assert isinstance(resp, AsyncIterable)
    assert interrupt is False
    assert (
        await resp.__aiter__().__anext__()
        == b"Request does not match any known command"
    )
    with pytest.raises(StopAsyncIteration):
        await resp.__aiter__().__anext__()


@pytest.mark.asyncio
@patch.object(
    MultiCommandInterpreter,
    "_execute_commands_in_message",
)
@pytest.mark.parametrize("second_interrupt", [False, True])
async def test_handle_wraps_responses_as_async_iterable_correctly(
    mock_execute_commands: AsyncMock,
    second_interrupt: bool,
    multi_command_interpreter: MultiCommandInterpreter,
):
    mock_execute_commands.return_value = (["resp1", "resp2"], [False, second_interrupt])
    resp, interrupt = await multi_command_interpreter.handle(AsyncMock(), "test")
    assert isinstance(resp, AsyncIterable)
    assert interrupt is second_interrupt
    assert await resp.__aiter__().__anext__() == "resp1"
    assert await resp.__aiter__().__anext__() == "resp2"
    with pytest.raises(StopAsyncIteration):
        await resp.__aiter__().__anext__()
