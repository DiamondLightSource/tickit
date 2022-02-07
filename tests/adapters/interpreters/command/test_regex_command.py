from typing import AnyStr, Optional, Tuple

import pytest

from tickit.adapters.interpreters.command import RegexCommand


@pytest.fixture
def regex_command(regex: AnyStr, interrupt: bool, format: Optional[str]):
    return RegexCommand(regex, interrupt, format)


def test_regex_command_registers_command():
    class TestAdapter:
        @RegexCommand("test")
        def test_method():
            pass

    assert isinstance(TestAdapter.test_method.__command__, RegexCommand)


@pytest.mark.parametrize(
    ["regex", "interrupt", "format", "message"],
    [
        (r"TestMessage", False, "utf-8", r"UnmatchedMessage".encode("utf-8")),
        (b"\\x01", False, None, b"\x02"),
    ],
)
def test_regex_command_parse_unmatched_returns_none(
    regex_command: RegexCommand, message: bytes
):
    assert regex_command.parse(message) is None


@pytest.mark.parametrize(
    ["regex", "interrupt", "format", "message", "expected"],
    [
        (r"TestMessage", False, "utf-8", r"TestMessage".encode("utf-8"), tuple()),
        (
            r"TestMessage(\d+)",
            False,
            "utf-8",
            r"TestMessage42".encode("utf-8"),
            ("42",),
        ),
        (b"\\x01", False, None, b"\x01", tuple()),
        (b"\\x01(.)", False, None, b"\x01\x02", (b"\x02",)),
    ],
)
def test_regex_command_parse_match_returns_args(
    regex_command: RegexCommand, message: bytes, expected: Tuple[object]
):
    assert expected == regex_command.parse(message)
