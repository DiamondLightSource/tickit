import pytest
from mock import ANY, AsyncMock

from tickit.adapters.interpreters.wrappers import BeheadingInterpreter


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_message, header_size, expected_beheaded_message",
    [
        ("headermessage", 6, "message"),
        (b"@\xbf\x00\x00\x00\x00\x00\x04message\r", 8, b"message\r"),
    ],
)
async def test_beheading_interpreter_removes_expected_number_of_characters(
    test_message, header_size, expected_beheaded_message
):
    mock_interpreter = AsyncMock()
    beheading_interpreter = BeheadingInterpreter(mock_interpreter, header_size)
    await beheading_interpreter.handle(AsyncMock(), test_message)
    mock_interpreter.handle.assert_called_once_with(ANY, expected_beheaded_message)
