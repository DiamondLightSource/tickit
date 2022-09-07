from typing import AnyStr, AsyncIterable, Tuple

from tickit.adapters.interpreters.utils import wrap_as_async_iterable
from tickit.core.adapter import Adapter, Interpreter


class JoiningInterpreter(Interpreter[AnyStr]):
    """A wrapper for an interpreter that combines responses.

    An interpreter wrapper class that takes the wrapped interpreter's response(s) to a
    message and combines them into a single response.
    """

    def __init__(
        self,
        interpreter: Interpreter[AnyStr],
        response_delimiter: AnyStr,
    ) -> None:
        """A decorator for an interpreter that combines multiple responses into one.

        Args:
            interpreter (Interpreter): The interpreter responding to a message.
            response_delimiter (AnyStr): The delimiter separating the responses to the
                individual responses when they are combined into a single response
                message.

        """
        super().__init__()
        self.interpreter: Interpreter[AnyStr] = interpreter
        self.response_delimiter: AnyStr = response_delimiter

    async def _combine_responses(
        self, responses: AsyncIterable[AnyStr]
    ) -> AsyncIterable[AnyStr]:
        """Combines results from handling multiple messages.

        Takes the responses from when the wrapped interpreter handles multiple messages
        and returns an appropriate composite repsonse and interrrupt. The composite
        response is the concatentation of each of the individual responses, the
        composite interrupt is a logical inclusive 'or' of all of the individual
        responses.

        Args:
            responses (AsyncIterable[AnyStr]): an async iterable of reply messages from
                the wrapped class' handle() method.

        Returns:
            AsyncIterable[AnyStr]:
                An asynchronous iterable containing a single reply message.
        """
        response_list = [response async for response in responses]
        response = self.response_delimiter.join(response_list)
        return wrap_as_async_iterable(response)

    async def handle(
        self, adapter: Adapter, message: AnyStr
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Merges the responses from an interpreter into a single message.

        Individual responses to the message are combined into a single response and
            returned.

        Args:
            adapter (Adapter): The adapter in which the function should be executed.
            message: (AnyStr): The message to be handled.

        Returns:
            Tuple[AsyncIterable[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterable of a single reply message and a
                flag indicating whether an interrupt should be raised by the adapter.
        """
        responses, interrupt = await self.interpreter.handle(adapter, message)
        resp = await self._combine_responses(responses)
        return resp, interrupt
