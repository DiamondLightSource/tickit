import re
from dataclasses import dataclass
from typing import AnyStr, Callable, Generic, Optional, Sequence


@dataclass(frozen=True)
class RegexCommand(Generic[AnyStr]):
    regex: AnyStr
    interrupt: bool = False
    format: Optional[str] = None

    def __call__(self, func: Callable) -> Callable:
        setattr(func, "__command__", self)
        return func

    def parse(self, data: bytes) -> Optional[Sequence[AnyStr]]:
        message = data.decode(self.format, "ignore").strip() if self.format else data
        if isinstance(message, type(self.regex)):
            match = re.fullmatch(self.regex, message)
            if match:
                # TODO: Check if matched args are of correct type
                return match.groups()
        return None
