from dataclasses import dataclass
from typing import AnyStr, Callable, Optional, Sequence

import pytest
from mock import AsyncMock, MagicMock, patch

from tickit.adapters.tcp import Command, CommandAdapter
from tickit.core.device import Device

_GET_TYPE_HINTS = "tickit.adapters.tcp.get_type_hints"


class ExampleAdapter(CommandAdapter):
    device: Device

    def test_method(self) -> None:
        pass


@pytest.fixture
def adapter() -> CommandAdapter:
    command_adapter = ExampleAdapter()
    return command_adapter


@pytest.fixture
def TestCommand():
    @dataclass(frozen=True)
    class TestCommand:
        command: bytes

        def __call__(self, func: Callable) -> Callable:
            setattr(func, "__command__", self)
            return func

        def parse(self, data: bytes) -> Optional[Sequence[str]]:
            if data == self.command:
                return ("arg1", "arg2")
            else:
                return None

    return TestCommand


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
async def test_command_adapter_handle_calls_func_with_args(adapter: ExampleAdapter):
    assert adapter is not None

    adapter.test_method = AsyncMock(
        __command__=MagicMock(
            Command,
            interrupt=False,
            parse=MagicMock(return_value=("arg1", "arg2")),
        ),
    )

    await adapter.handle(b"\x01")

    adapter.test_method.assert_awaited_once_with("arg1", "arg2")


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
async def test_command_adapter_handle_returns_iterable_reply(adapter: ExampleAdapter):
    reply = AsyncMock(__aiter__=MagicMock(), __anext__=AsyncMock())
    adapter.test_method = AsyncMock(
        __command__=MagicMock(
            Command,
            interrupt=False,
            parse=MagicMock(return_value=("arg1", "arg2")),
        ),
        return_value=reply,
    )
    assert reply == (await adapter.handle(b"\x01"))[0]


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
async def test_command_adapter_handle_wraps_non_iterable_reply(adapter: ExampleAdapter):
    reply = MagicMock("TestReply")
    adapter.test_method = AsyncMock(
        __command__=MagicMock(
            Command,
            interrupt=False,
            parse=MagicMock(return_value=("arg1", "arg2")),
        ),
        return_value=reply,
    )
    assert reply == await (await adapter.handle(b"\x01"))[0].__aiter__().__anext__()


@patch(
    _GET_TYPE_HINTS,
    lambda _: {"arg1": str, "arg2": str},
)
@pytest.mark.asyncio
@pytest.mark.parametrize("interrupt", [True, False])
async def test_command_adapter_handle_returns_interrupt(
    adapter: ExampleAdapter, interrupt: bool
):
    adapter.test_method = AsyncMock(
        __command__=MagicMock(
            Command,
            interrupt=interrupt,
            parse=MagicMock(return_value=("arg1", "arg2")),
        ),
        return_value="DummyReply",
    )
    assert interrupt == (await adapter.handle(b"\x01"))[1]


@pytest.mark.asyncio
@pytest.mark.parametrize("interrupt", [True, False])
async def test_command_adapter_handle_skips_unparsed(
    adapter: ExampleAdapter, interrupt: bool
):
    adapter.test_method = AsyncMock(
        __command__=MagicMock(
            Command, interrupt=interrupt, parse=MagicMock(return_value=None)
        ),
        return_value="DummyReply",
    )
    assert (
        b"Request does not match any known command"
        == await (await adapter.handle("TestCommand".encode("utf-8")))[0]
        .__aiter__()
        .__anext__()
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command, response_message",
    [
        ("UnknownString", "Request does not match any known command"),
        (b"UnknownBytes", b"Request does not match any known command"),
    ],
)
async def test_command_adapter_handle_returns_message_for_no_commands(
    adapter: ExampleAdapter,
    command: AnyStr,
    response_message: AnyStr,
):
    response = await adapter.handle(command)
    message = await response[0].__anext__()
    assert message == response_message
