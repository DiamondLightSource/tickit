import re
from dataclasses import dataclass
from typing import AnyStr, Callable, Generic, Optional, Sequence, Tuple, cast


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

    def parse(self, data: AnyStr) -> Optional[Tuple[Sequence[AnyStr], int, int, int]]:
        """Performs message decoding and regex matching to match and extract arguments.

        A method which performs message decoding accoridng to the command formatting
        string, checks for a regular expression match using re.search. If a match is
        found, it returns a sequence of function arguments together with some integers
        giving information about the match, otherwise the method returns None.

        Args:
            data (bytes): The message data to be parsed.

        Returns:
            Optional[Tuple[Sequence[AnyStr], int, int, int]]:
                If a match is found a sequence of function arguments is returned,
                together with three integers corresponding to the start and end indices
                of the match with respect to the (foramtted) data as well as the length
                of the (formatted) data; otherwise the method returns None.
        """
        to_format = (
            self.format and isinstance(data, bytes) and isinstance(self.regex, str)
        )
        if to_format:  # isinstance(data, bytes) and isinstance(self.regex, str):
            # We only want to format if matching a string pattern against bytes data.
            # Formatting consists of encoding the pattern and stripping the data of
            # ascii whitespace.
            regex_formatted = cast(str, self.regex).encode(
                cast(str, self.format), "ignore"
            )
            regex_formatted = regex_formatted
            message = data.strip()
        else:
            regex_formatted = cast(bytes, self.regex)
            message = data
        if isinstance(message, type(regex_formatted)):
            match = re.search(regex_formatted, message)
            if match is None:
                return None
            match_groups = match.groups()
            match_start = match.start()
            match_end = match.end()
            formatted_message_length = len(message)
            if to_format:
                match_groups = tuple(
                    (group.decode(cast(str, self.format)) for group in match_groups)
                )
            return match_groups, match_start, match_end, formatted_message_length
        return None
