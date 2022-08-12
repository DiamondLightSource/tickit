import functools
from typing import AnyStr, AsyncIterable, List, Tuple, overload

from tickit.adapters.interpreters.utils import wrap_as_async_iterable
from tickit.core.adapter import Adapter, Interpreter


class SplittingInterpreter(Interpreter[AnyStr]):
    """An wrapper for an interpreter that splits a single message into multiple.

    An interpreter wrapper class that takes a message, splits it according to a given
    delimiter, and passes on the resulting sub-messages individually on to the
    wrapped interpreter. The individual responses to the sub-messages are combined into
    a single response.
    """

    @overload
    def __init__(self, interpreter: Interpreter[AnyStr]) -> None:  # noqa: D105
        pass

    @overload
    def __init__(
        self, interpreter: Interpreter[AnyStr], delimiter: AnyStr
    ) -> None:  # noqa: D105
        pass

    def __init__(self, interpreter: Interpreter[AnyStr], delimiter=b" ") -> None:
        """A decorator for an interpreter that splits a message into multiple sub-messages.

        Args:
            interpreter (Interpreter): The interpreter messages are passed on to.
            delimiter (AnyStr): The delimiter by which the message is split up.

        """
        super().__init__()
        self.interpreter: Interpreter[AnyStr] = interpreter
        self.delimiter: AnyStr = delimiter

    async def _handle_individual_messages(
        self, adapter: Adapter, individual_messages: List[AnyStr]
    ) -> List[Tuple[AsyncIterable[AnyStr], bool]]:
        results = [
            await self.interpreter.handle(adapter, message)
            for message in individual_messages
        ]
        return results

    @staticmethod
    async def _get_response_and_interrupt_from_individual_results(
        results: List[Tuple[AsyncIterable[AnyStr], bool]]
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Combines results from handling multiple messages.

        Takes the responses from when the wrapped interpreter handles multiple messages
        and returns an appropriate composite repsonse and interrrupt. The composite
        response is the concatentation of each of the individual responses, the
        composite interrupt is a logical inclusive 'or' of all of the individual
        responses.

        Args:
            results (List[Tuple[AsyncIterable[AnyStr], bool]]): a list of returned
                values from the wrapped class' handle() method.

        Returns:
            Tuple[AsyncIterable[AnyStr], bool]:
                A tuple of the asynchronous iterable of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        individual_responses, individual_interrupts = zip(*results)

        response_list = [
            response
            for response_gen in individual_responses
            async for response in response_gen
        ]
        response = functools.reduce(lambda a, b: a + b, response_list)
        resp = wrap_as_async_iterable(response)

        interrrupt = any(individual_interrupts)

        return resp, interrrupt

    async def handle(
        self, adapter: Adapter, message: AnyStr
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Splits a message and passes the resulting sub-messages on to an interpreter.

        Splits a given message and passes the resulting sub-messages on to an
        interpreter. The responses to the individual sub-messages are then combined
        into a single response and returned.

        Args:
            adapter (Adapter): The adapter in which the function should be executed
            message: (AnyStr): The message to be split up and handled.

        Returns:
            Tuple[AsyncIterable[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterable of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        individual_messages = message.split(self.delimiter)

        results = await self._handle_individual_messages(adapter, individual_messages)

        (
            resp,
            interrupt,
        ) = await self._get_response_and_interrupt_from_individual_results(results)

        return resp, interrupt
