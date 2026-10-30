from typing import AnyStr

import pytest

from tickit.adapters.specifications import RegexCommand


@pytest.fixture
def regex_command(regex: AnyStr, interrupt: bool, format: str | None):
    return RegexCommand(regex, interrupt, format)


def test_regex_command_registers_command():
    class TestAdapter:
        @RegexCommand("test", format="utf-8")
        def test_method():
            pass

    assert isinstance(TestAdapter.test_method.__command__, RegexCommand)


@pytest.mark.parametrize(
    ["regex", "interrupt", "format", "message"],
    [
        (r"TestMessage", False, "utf-8", rb"UnmatchedMessage"),
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
        (r"TestMessage", False, "utf-8", rb"TestMessage", tuple()),
        (
            r"TestMessage(\d+)",
            False,
            "utf-8",
            rb"TestMessage42",
            ("42",),
        ),
        (b"\\x01", False, None, b"\x01", tuple()),
        (b"\\x01(.)", False, None, b"\x01\x02", (b"\x02",)),
        (r"Test\((\d)\)", False, "utf-8", b"Test(4)\n", ("4",)),
        (r"Test\((\d)\)", False, "utf-8", b"Test(3)\r\n", ("3",)),
    ],
)
def test_regex_command_parse_match_returns_args(
    regex_command: RegexCommand, message: bytes, expected: tuple[object]
):
    assert expected == regex_command.parse(message)
