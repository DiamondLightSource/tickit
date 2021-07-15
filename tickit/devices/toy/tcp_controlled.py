import re
from typing import Dict, Iterable, Set

from tickit.adapters import TcpAdapter
from tickit.core.adapter import Adapter
from tickit.core.device import UpdateEvent
from tickit.core.typedefs import IoId
from tickit.utils.compat.functools import cached_property


class TcpControlled:
    tcp_server = TcpAdapter()
    observed = 0
    unobserved = 0

    @property
    def outputs(self) -> Set[IoId]:
        return {"observed"}

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        self.tcp_server.link(self)
        return [self.tcp_server]

    def update(self, delta: int, inputs: Dict[str, object]) -> UpdateEvent:
        return UpdateEvent({"observed": self.observed}, None)

    @tcp_server.command(r"O")
    def get_observed(self, message: str) -> str:
        return self.observed

    @tcp_server.command(r"O=\d+\.?\d*", interrupt=True)
    def set_observed(self, message: str) -> None:
        self.observed = re.search(r"\d+\.?\d*", message).group(0)

    @tcp_server.command(r"U")
    def get_unobserved(self, message: str) -> str:
        return self.unobserved

    @tcp_server.command(r"U=\d+\.?\d*")
    def set_unobserved(self, message: str) -> None:
        self.unobserved = re.search(r"\d+\.?\d*", message).group(0)
