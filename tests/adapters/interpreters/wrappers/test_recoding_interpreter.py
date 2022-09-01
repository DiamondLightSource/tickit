import pytest
from mock import ANY, AsyncMock

from tickit.adapters.interpreters.wrappers import (
    DecodingInterpreter,
    EncodingInterpreter,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("message, encoding", [("hello", "utf-8"), ("test", "utf-32")])
async def test_decoding_interpreter_decodes_bytes_correctly(message, encoding):
    mock_interpreter = AsyncMock()
    decoding_interpreter = DecodingInterpreter(mock_interpreter, encoding=encoding)
    await decoding_interpreter.handle(AsyncMock(), message.encode(encoding))
    mock_interpreter.handle.assert_called_once_with(ANY, message)


@pytest.mark.asyncio
async def test_decoding_interpreter_handles_strings_correctly():
    mock_interpreter = AsyncMock()
    decoding_interpreter = DecodingInterpreter(mock_interpreter)
    await decoding_interpreter.handle(AsyncMock(), "test")
    mock_interpreter.handle.assert_called_once_with(ANY, "test")


@pytest.mark.asyncio
async def test_decoding_interpreter_default_encoding():
    mock_interpreter = AsyncMock()
    decoding_interpreter = DecodingInterpreter(mock_interpreter)
    await decoding_interpreter.handle(AsyncMock(), "test".encode("utf-8"))
    mock_interpreter.handle.assert_called_once_with(ANY, "test")


@pytest.mark.asyncio
@pytest.mark.parametrize("message, encoding", [("hello", "utf-8"), ("test", "utf-32")])
async def test_encoding_interpreter_encodes_strings_correctly(message, encoding):
    mock_interpreter = AsyncMock()
    encoding_interpreter = EncodingInterpreter(mock_interpreter, encoding=encoding)
    await encoding_interpreter.handle(AsyncMock(), message)
    mock_interpreter.handle.assert_called_once_with(ANY, message.encode(encoding))


@pytest.mark.asyncio
async def test_encoding_interpreter_handles_bytes_corrrectly():
    mock_interpreter = AsyncMock()
    encoding_interpreter = EncodingInterpreter(mock_interpreter)
    await encoding_interpreter.handle(AsyncMock(), b"test")
    mock_interpreter.handle.assert_called_once_with(ANY, b"test")


@pytest.mark.asyncio
async def test_encoding_interpreter_default_encoding():
    mock_interpreter = AsyncMock()
    encoding_interpreter = EncodingInterpreter(mock_interpreter)
    await encoding_interpreter.handle(AsyncMock(), "test")
    mock_interpreter.handle.assert_called_once_with(ANY, "test".encode("utf-8"))
