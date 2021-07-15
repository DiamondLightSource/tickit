from typing import Dict, Iterable, Optional, Set, Tuple

from tickit.core.adapter import Adapter
from tickit.core.typedefs import IoId
from tickit.utils.compat.functools import cached_property
from tickit.utils.compat.typing import Protocol, runtime_checkable


@runtime_checkable
class Device(Protocol):
    @property
    def outputs(self) -> Set[IoId]:
        ...

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        ...

    def update(
        self, delta: float, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        ...
