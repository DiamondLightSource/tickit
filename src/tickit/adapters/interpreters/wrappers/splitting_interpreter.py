import re
from typing import AnyStr, AsyncIterable, List, Tuple

from tickit.adapters.interpreters.utils import wrap_messages_as_async_iterable
from tickit.core.adapter import Adapter, Interpreter


class SplittingInterpreter(Interpreter[AnyStr]):
    """A wrapper for an interpreter that splits a single message into multiple.

    An interpreter wrapper class that takes a message, splits it according to a given
    delimiter, and passes on the resulting sub-messages individually on to the
    wrapped interpreter.
    """

    def __init__(
        self,
        interpreter: Interpreter[AnyStr],
        message_delimiter: AnyStr,
    ) -> None:
        """An interpreter decorator that splits a message into multiple sub-messages.

        Args:
            interpreter (Interpreter): The interpreter messages are passed on to.
            message_delimiter (AnyStr): The delimiter by which the message is split up.
                Can be a regex pattern. Must be of the same type as the message.
        """
        super().__init__()
        self.interpreter: Interpreter[AnyStr] = interpreter
        self.message_delimiter: AnyStr = message_delimiter

    async def _handle_individual_messages(
        self, adapter: Adapter, individual_messages: List[AnyStr]
    ) -> List[Tuple[AsyncIterable[AnyStr], bool]]:
        results = [
            await self.interpreter.handle(adapter, message)
            for message in individual_messages
        ]
        return results

    async def _collect_responses(
        self, results: List[Tuple[AsyncIterable[AnyStr], bool]]
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Combines results from handling multiple messages.

        Takes the responses from when the wrapped interpreter handles multiple messages
        and returns an appropriate composite repsonse and interrrupt. The response is
        an asyncronous iterable of each of the individual responses, the composite
        interrupt is a logical inclusive 'or' of all of the individual interrupts.

        Args:
            results (List[Tuple[AsyncIterable[AnyStr], bool]]): a list of returned
                values from the wrapped class' handle() method.

        Returns:
            Tuple[AsyncIterable[AnyStr], bool]:
                A tuple of the asynchronous iterable of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        individual_responses, individual_interrupts = zip(*results)

        responses = [
            response
            for response_gen in individual_responses
            async for response in response_gen
        ]

        resp = wrap_messages_as_async_iterable(responses)
        interrrupt = any(individual_interrupts)
        return resp, interrrupt

    async def handle(
        self, adapter: Adapter, message: AnyStr
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Splits a message and passes the resulting sub-messages on to an interpreter.

        Splits a given message and passes the resulting sub-messages on to an
        interpreter. The responses to the individual sub-messages are then returned.

        Args:
            adapter (Adapter): The adapter in which the function should be executed
            message: (AnyStr): The message to be split up and handled.

        Returns:
            Tuple[AsyncIterable[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterable of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        individual_messages = [
            msg for msg in re.split(self.message_delimiter, message) if msg is not None
        ]

        results = await self._handle_individual_messages(adapter, individual_messages)

        return await self._collect_responses(results)
