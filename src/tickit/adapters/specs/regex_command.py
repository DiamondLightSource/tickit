from dataclasses import InitVar, dataclass, field
from re import Pattern, compile
from typing import AnyStr, Callable, Generic, Optional, Sequence


@dataclass
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

    regex: InitVar[AnyStr]
    interrupt: bool = False
    format: InitVar[Optional[str]] = None
    pattern: Pattern[AnyStr] = field(init=False)
    convert: Callable[[bytes], AnyStr] = field(init=False)

    def __post_init__(self, regex: AnyStr, format: Optional[str]):
        # The type checking fails here as it can't determine that the return
        # type matches the regex type. The isinstance should narrow the AnyStr
        # type but doesn't
        if isinstance(regex, str):
            if format is None:
                raise ValueError(
                    "If regex is a string, format is required to decode input"
                )
            self.convert = lambda b: b.decode(format).strip()  # type: ignore
        else:
            self.convert = lambda b: b  # type: ignore

        self.pattern = compile(regex)

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

        A method which performs message decoding according to the command formatting
        string, checks for a full regular expression match and returns a sequence of
        function arguments if a match is found, otherwise the method returns None.

        Args:
            data (bytes): The message data to be parsed.

        Returns:
            Optional[Sequence[AnyStr]]:
                If a full match is found a sequence of function arguments is returned,
                otherwise the method returns None.
        """
        message = self.convert(data)
        match = self.pattern.fullmatch(message)
        if match:
            return match.groups()
        return None
