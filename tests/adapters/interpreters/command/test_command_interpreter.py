from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple

import pytest
from mock import AsyncMock, MagicMock, patch

from tickit.adapters.interpreters.command import CommandInterpreter
from tickit.adapters.interpreters.command.command_interpreter import Command
from tickit.core.adapter import Adapter

_GET_TYPE_HINTS = (
    "tickit.adapters.interpreters.command.command_interpreter.get_type_hints"
)

MOCK_PARSE_RETURN = (("arg1", "arg2"), 1, 2, 2)


@pytest.fixture
def command_interpreter():
    return CommandInterpreter()


@pytest.fixture
def TestCommand():
    @dataclass(frozen=True)
    class TestCommand:
        command: bytes

        def __call__(self, func: Callable) -> Callable:
            setattr(func, "__command__", self)
            return func

        def parse(self, data: bytes) -> Optional[Tuple[Sequence[str], int, int, int]]:
            if data == self.command:
                return MOCK_PARSE_RETURN
            else:
                return None

    return TestCommand


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
async def test_command_interpreter_handle_calls_func_with_args(
    command_interpreter: CommandInterpreter,
):
    test_adapter = MagicMock(
        Adapter,
        test_method=AsyncMock(
            __command__=MagicMock(
                Command,
                interrupt=False,
                parse=MagicMock(return_value=MOCK_PARSE_RETURN),
            ),
        ),
    )
    await command_interpreter.handle(test_adapter, b"\x01")
    test_adapter.test_method.assert_awaited_once_with("arg1", "arg2")


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
async def test_command_interpreter_handle_returns_iterable_reply(
    command_interpreter: CommandInterpreter,
):
    reply = AsyncMock(__aiter__=MagicMock(), __anext__=AsyncMock())
    test_adapter = MagicMock(
        Adapter,
        test_method=AsyncMock(
            __command__=MagicMock(
                Command,
                interrupt=False,
                parse=MagicMock(return_value=MOCK_PARSE_RETURN),
            ),
            return_value=reply,
        ),
    )
    assert reply == (await command_interpreter.handle(test_adapter, b"\x01"))[0]


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
async def test_command_interpreter_handle_wraps_non_iterable_reply(
    command_interpreter: CommandInterpreter,
):
    reply = MagicMock("TestReply")
    test_adapter = MagicMock(
        Adapter,
        test_method=AsyncMock(
            __command__=MagicMock(
                Command,
                interrupt=False,
                parse=MagicMock(return_value=MOCK_PARSE_RETURN),
            ),
            return_value=reply,
        ),
    )
    assert (
        reply
        == await (await command_interpreter.handle(test_adapter, b"\x01"))[0]
        .__aiter__()
        .__anext__()
    )


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
@pytest.mark.parametrize("interrupt", [True, False])
async def test_command_interpreter_handle_returns_interupt(
    command_interpreter: CommandInterpreter, interrupt: bool
):
    test_adapter = MagicMock(
        Adapter,
        test_method=AsyncMock(
            __command__=MagicMock(
                Command,
                interrupt=interrupt,
                parse=MagicMock(return_value=MOCK_PARSE_RETURN),
            ),
            return_value="DummyReply",
        ),
    )
    assert interrupt == (await command_interpreter.handle(test_adapter, b"\x01"))[1]


@pytest.mark.asyncio
@pytest.mark.parametrize("interrupt", [True, False])
async def test_command_interpreter_handle_skips_unparsed(
    command_interpreter: CommandInterpreter, interrupt: bool
):
    test_adapter = MagicMock(
        Adapter,
        test_method=AsyncMock(
            __command__=MagicMock(
                Command, interrupt=interrupt, parse=MagicMock(return_value=None)
            ),
            return_value="DummyReply",
        ),
    )
    assert (
        b"Request does not match any known command"
        == await (
            await command_interpreter.handle(
                test_adapter, "TestCommand".encode("utf-8")
            )
        )[0]
        .__aiter__()
        .__anext__()
    )


@pytest.mark.asyncio
async def test_command_interpreter_handle_returns_message_for_no_commands(
    command_interpreter: CommandInterpreter,
):
    test_adapter = MagicMock(Adapter)
    assert (
        b"Request does not match any known command"
        == await (
            await command_interpreter.handle(
                test_adapter, "TestCommand".encode("utf-8")
            )
        )[0]
        .__aiter__()
        .__anext__()
    )


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
@pytest.mark.parametrize("match_end, expected_num_awaits", [(2, 0), (3, 1)])
async def test_command_interpreter_matches_commands_against_full_message(
    command_interpreter: CommandInterpreter, match_end: int, expected_num_awaits: int
):
    test_adapter = MagicMock(
        Adapter,
        test_method=AsyncMock(
            __command__=MagicMock(
                Command,
                interrupt=False,
                parse=MagicMock(return_value=(("arg1", "arg2"), 1, match_end, 3)),
            ),
        ),
    )
    await command_interpreter.handle(test_adapter, b"\x01")
    assert test_adapter.test_method.await_count == expected_num_awaits


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": int, "arg2": float},
)
@pytest.mark.asyncio
async def test_command_interpreter_converts_args_to_types_correctly(
    command_interpreter: CommandInterpreter,
):
    test_adapter = MagicMock(
        Adapter,
        test_method=AsyncMock(
            __command__=MagicMock(
                Command,
                interrupt=False,
                parse=MagicMock(return_value=(("1", "1.0"), 1, 3, 3)),
            ),
        ),
    )
    await command_interpreter.handle(test_adapter, b"\x01")
    assert test_adapter.test_method.awaited_with([int(1), float(1.0)])
