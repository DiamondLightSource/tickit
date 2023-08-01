from typing import AnyStr, AsyncIterator, Tuple

from tickit.adapters.tcp import CommandAdapter
from tickit.core.adapter import Interpreter


class BeheadingWrapper(Interpreter[AnyStr]):
    """A wrapper for CommandAdapter which strips a header from a message.

    An CommandAdapter wrapper that takes a message, strips off a header of a fixed size
    and passes the stripped message on to the wrapped CommandAdapter
    """

    def __init__(self, adapter: CommandAdapter[AnyStr], header_size: int) -> None:
        """A wrapper for an CommandAdapter which strips a header from a message.

        Args:
            adapter (CommandAdapter): The adapter the message is passed on to
                after the header is stripped.
            header_size (int): The number of characters in the header.
        """
        super().__init__()
        self.adapter: CommandAdapter[AnyStr] = adapter
        self.header_size: int = header_size

    async def handle(self, message: AnyStr) -> Tuple[AsyncIterator[AnyStr], bool]:
        """Removes a header from a message and passes the message on to an adapter.

        Args:
            message: (AnyStr): The handled message, of which the header is removed.

        Returns:
            Tuple[AsyncIterator[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterator of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        message = message[self.header_size :]
        return await self.adapter.handle(message)
