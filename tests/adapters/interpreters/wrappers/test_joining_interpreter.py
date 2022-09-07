from typing import AnyStr, AsyncIterable, List

import pytest
from mock import AsyncMock

from tickit.adapters.interpreters.wrappers import JoiningInterpreter


@pytest.mark.asyncio
async def test_joining_interpreter_concatenates_as_expected():
    async def multi_resp(msgs: List[AnyStr]) -> AsyncIterable[AnyStr]:
        for msg in msgs:
            yield msg

    mock_interpreter = AsyncMock()
    mock_interpreter.handle.return_value = multi_resp(["one", "two", "three"]), True
    joining_interpreter = JoiningInterpreter(mock_interpreter, response_delimiter="-")
    result, _ = await joining_interpreter.handle(AsyncMock(), "test")
    assert [msg async for msg in result] == ["one-two-three"]
