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
    result = regex_command.parse(message)
    assert result is not None
    args, _, _, _ = result
    assert expected == args


@pytest.mark.parametrize(
    ["regex", "interrupt", "format", "message", "expected"],
    [
        (r"(Test)Message", False, None, r"TestMessage", ("Test",)),
        (b"\\x01(.)", False, None, b"\x01\x02", (b"\x02",)),
    ],
)
def test_regex_command_parse_can_take_anystr(
    regex_command: RegexCommand, message: AnyStr, expected
):
    result = regex_command.parse(message)
    assert result is not None
    args, _, _, _ = result
    assert expected == args


@pytest.mark.parametrize(
    ["regex", "interrupt", "format", "message", "expected_end_of_match"],
    [
        (r"Test", False, None, r"TestMessage", 4),
        (r"Test", False, "utf-32", "TestMessage".encode("utf-32"), 20),
    ],
)
def test_parse_gives_right_end(
    regex_command: RegexCommand, message: AnyStr, expected_end_of_match
):
    result = regex_command.parse(message)
    assert result is not None
    _, _, end, _ = result
    assert end == expected_end_of_match


@pytest.mark.parametrize(
    ["regex", "interrupt", "format", "message", "expected_end_of_match"],
    [
        (r"Test", False, None, r"\nTest\r\n", 6),
        (r"Test", False, "utf-8", b"\nTest\r\n", 4),
    ],
)
def test_parse_strips_correctly_when_formatting(
    regex_command: RegexCommand, message: AnyStr, expected_end_of_match
):
    result = regex_command.parse(message)
    assert result is not None
    _, _, end, _ = result
    assert end == expected_end_of_match


@pytest.mark.parametrize(
    ["regex", "interrupt", "format", "message", "full_match_expected"],
    [
        (r"Test", False, None, r"\nTest\r\n", False),
        (r"Test", False, "utf-8", b"\nTest\r\n", True),
        (rb"Test", False, "utf-8", b"\nTest\r\n", False),
        (rb"Test", False, None, b"\nTest\r\n", False),
    ],
)
def test_parse_gives_correct_whole_matches(
    regex_command: RegexCommand, message: AnyStr, full_match_expected
):
    result = regex_command.parse(message)
    assert result is not None
    _, _, end, message_length = result
    full_match = end == message_length
    assert full_match == full_match_expected
