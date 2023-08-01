from re import Pattern, compile
from typing import AnyStr, AsyncIterator, List, Tuple

from tickit.adapters.tcp import CommandAdapter
from tickit.adapters.utils import wrap_messages_as_async_iterator
from tickit.core.adapter import Interpreter


class SplittingWrapper(Interpreter[AnyStr]):
    """A wrapper for the CommandAdapter that splits a single message into multiple.

    An CommandAdapter wrapper class that takes a message, splits it according to a given
    delimiter, and passes on the resulting sub-messages individually on to the
    wrapped CommandAdapter.
    """

    def __init__(
        self,
        adapter: CommandAdapter[AnyStr],
        message_delimiter: AnyStr,
    ) -> None:
        """An CommandAdapter decorator that splits a message into multiple sub-messages.

        Args:
            adapter (Interpreter): The CommandAdapter messages are passed on to.
            message_delimiter (AnyStr): The delimiter by which the message is split up.
                Can be a regex pattern. Must be of the same type as the message.
        """
        super().__init__()
        self.adapter: CommandAdapter[AnyStr] = adapter
        self.delimeter: Pattern[AnyStr] = compile(message_delimiter)

    async def _handle_individual_messages(
        self, individual_messages: List[AnyStr]
    ) -> List[Tuple[AsyncIterator[AnyStr], bool]]:
        results = [
            await self.adapter.handle(message) for message in individual_messages
        ]
        return results

    async def _collect_responses(
        self, results: List[Tuple[AsyncIterator[AnyStr], bool]]
    ) -> Tuple[AsyncIterator[AnyStr], bool]:
        """Combines results from handling multiple messages.

        Takes the responses from when the wrapped CommandAdapter handles multiple
        messages and returns an appropriate composite response and interrupt. The
        response is an asynchronous iterator of each of the individual responses,
        the composite interrupt is a logical inclusive 'or' of all of the individual
        interrupts.

        Args:
            results (List[Tuple[AsyncIterator[AnyStr], bool]]): a list of returned
                values from the wrapped class' handle() method.

        Returns:
            Tuple[AsyncIterator[AnyStr], bool]:
                A tuple of the asynchronous iterator of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        individual_responses, individual_interrupts = zip(*results)

        responses = [
            response
            for response_gen in individual_responses
            # type checking can't figure out the return types of zip(*args)
            async for response in response_gen  # type: ignore
        ]

        resp = wrap_messages_as_async_iterator(responses)
        interrupt = any(individual_interrupts)
        return resp, interrupt

    async def handle(self, message: AnyStr) -> Tuple[AsyncIterator[AnyStr], bool]:
        """Splits a message and passes the resulting sub-messages to a CommandAdapter.

        Splits a given message and passes the resulting sub-messages on to an
        CommandAdapter. The responses to the individual sub-messages are then returned.

        Args:
            adapter (Adapter): The adapter in which the function should be executed
            message: (AnyStr): The message to be split up and handled.

        Returns:
            Tuple[AsyncIterator[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterator of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        individual_messages = [
            msg
            for msg in self.delimeter.split(message)
            if msg  # Discard empty strings and None
        ]

        results = await self._handle_individual_messages(individual_messages)

        return await self._collect_responses(results)

    def after_update(self) -> None:
        ...
