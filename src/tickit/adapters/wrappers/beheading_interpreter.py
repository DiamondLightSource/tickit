from typing import AnyStr, AsyncIterable, Tuple

from tickit.core.adapter import Adapter, Interpreter


class BeheadingInterpreter(Interpreter[AnyStr]):
    """A wrapper for an interpreter which strips a header from a message.

    An interpreter wrapper that takes a message, strips off a header of a fixed size
    and passes the stripped message on to the wrapped interpreter
    """

    def __init__(self, interpreter: Interpreter[AnyStr], header_size: int) -> None:
        """A wrapper for an interpreter which strips a header from a message.

        Args:
            interpreter (Interpreter): The interpreter the message is passed on to
                after the header is stripped.
            header_size (int): The number of characters in the header.
        """
        super().__init__()
        self.interpreter: Interpreter[AnyStr] = interpreter
        self.header_size: int = header_size

    async def handle(
        self, adapter: Adapter, message: AnyStr
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Removes a header from a message and passes the message on to an interpreter.

        Args:
            adapter (Adapter): The adapter in which the function should be executed
            message: (AnyStr): The handled message, of which the header is removed.

        Returns:
            Tuple[AsyncIterable[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterable of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        message = message[self.header_size :]
        return await self.interpreter.handle(adapter, message)
