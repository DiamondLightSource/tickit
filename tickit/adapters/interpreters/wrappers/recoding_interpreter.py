from typing import AnyStr, AsyncIterable, Tuple, cast

from tickit.core.adapter import Adapter, Interpreter


class DecodingInterpreter(Interpreter[AnyStr]):
    """A wrapper for an interpreter that decodes messages.

    An interpreter wrapper class that recieves messages, decodes them, and then passes
    them on to the wrapped interpreter to handle.
    """

    def __init__(
        self, interpreter: Interpreter[AnyStr], encoding: str = "utf-8"
    ) -> None:
        """A wrapper for an interpreter that decodes messages.

        Args:
            interpreter (Interpreter): The interpreter decoded messages are passed to.
            encoding (str): The encoding with which to decode the incoming message.
        """
        self.interpreter: Interpreter[AnyStr] = interpreter
        self.encoding = encoding
        super().__init__()

    async def handle(
        self, adapter: Adapter, message: AnyStr
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Decodes a message and passes it on to be handled by the wrapped interpreter.

        Args:
            adapter (Adapter): The adapter in which the function should be executed.
            message: (AnyStr): The message to be handled.

        Returns:
            Tuple[AsyncIterable[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterable of replies and a flag indicating
                whether an interrupt should be raised by the adapter.
        """
        if type(message) == bytes:
            decoded_message = cast(bytes, message).decode(encoding=self.encoding)
        else:
            decoded_message = cast(str, message)
        return await self.interpreter.handle(adapter, cast(AnyStr, decoded_message))


class EncodingInterpreter(Interpreter[AnyStr]):
    """A wrapper for an interpreter that encodes messages.

    An interpreter wrapper class that recieves messages, encodes them, and then passes
    them on to the wrapped interpreter to handle.
    """

    def __init__(
        self, interpreter: Interpreter[AnyStr], encoding: str = "utf-8"
    ) -> None:
        """A wrapper for an interpreter that encodes messages.

        Args:
            interpreter (Interpreter): The interpreter encoded messages are passed to.
            encoding (str): The encoding with which to encode the incoming message.
        """
        self.interpreter: Interpreter[AnyStr] = interpreter
        self.encoding = encoding
        super().__init__()

    async def handle(
        self, adapter: Adapter, message: AnyStr
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Encodes a message and passes it on to be handled by the wrapped interpreter.

        Args:
            adapter (Adapter): The adapter in which the function should be executed.
            message: (AnyStr): The message to be handled.

        Returns:
            Tuple[AsyncIterable[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterable of replies and a flag indicating
                whether an interrupt should be raised by the adapter.
        """
        if type(message) == str:
            encoded_message = cast(str, message).encode(encoding=self.encoding)
        else:
            encoded_message = cast(bytes, message)
        return await self.interpreter.handle(adapter, cast(AnyStr, encoded_message))
