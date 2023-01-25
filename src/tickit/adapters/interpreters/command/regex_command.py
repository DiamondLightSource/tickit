import re
from dataclasses import dataclass
from typing import AnyStr, Callable, Generic, Optional, Sequence


@dataclass(frozen=True)
class RegexCommand(Generic[AnyStr]):
    """A decorator to register an adapter method as a regex parsed command.

    Args:
        regex (Union[bytes, str]): The regular expression pattern which must be
            matched in full, with groups used to extract command arguments.
        interrupt (bool): A flag indicating whether calling of the method should
            raise an adapter interrupt. Defaults to False.
        format (Optional[str]): The message decoding format to be used for string
            based interpretation. Defaults to None.

    Returns:
        Callable:
            A decorator which registers the adapter method as a message handler.
    """

    regex: AnyStr
    interrupt: bool = False
    format: Optional[str] = None

    def __call__(self, func: Callable) -> Callable:
        """A decorator which registers the adapter method as a message handler.

        Args:
            func (Callable): The adapter method to be registered as a command.

        Returns:
            Callable: The registered adapter method.
        """
        setattr(func, "__command__", self)
        return func

    def parse(self, data: bytes) -> Optional[Sequence[AnyStr]]:
        """Performs message decoding and regex matching to match and extract arguments.

        A method which performs message decoding accoridng to the command formatting
        string, checks for a full regular expression match and returns a sequence of
        function arguments if a match is found, otherwise the method returns None.

        Args:
            data (bytes): The message data to be parsed.

        Returns:
            Optional[Sequence[AnyStr]]:
                If a full match is found a sequence of function arguments is returned,
                otherwise the method returns None.
        """
        message = data.decode(self.format, "ignore").strip() if self.format else data
        if isinstance(message, type(self.regex)):
            match = re.fullmatch(self.regex, message)
            if match:
                return match.groups()
        return None
