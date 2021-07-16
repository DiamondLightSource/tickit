import re
from typing import Iterable, Set

from tickit.adapters import TcpAdapter
from tickit.core.adapter import Adapter
from tickit.core.device import Device, UpdateEvent
from tickit.core.typedefs import IoId, State
from tickit.utils.compat.functools_compat import cached_property


class TcpControlled(Device):
    tcp_server = TcpAdapter()
    observed: int = 0
    unobserved: int = 0

    @property
    def outputs(self) -> Set[IoId]:
        return {IoId("observed")}

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        self.tcp_server.link(self)
        return [self.tcp_server]

    def update(self, delta: int, inputs: State) -> UpdateEvent:
        return UpdateEvent(State({IoId("observed"): self.observed}), None)

    @tcp_server.command(r"O")
    def get_observed(self, message: str) -> str:
        return str(self.observed)

    @tcp_server.command(r"O=\d+\.?\d*", interrupt=True)
    def set_observed(self, message: str) -> str:
        try:
            match = re.search(r"\d+\.?\d*", message)
            if not match:
                return "Could not extract value from command"
            self.observed = int(match.group(0))
            return "Observed set to {}".format(self.observed)
        except ValueError:
            return "Command gave invalid value"

    @tcp_server.command(r"U")
    def get_unobserved(self, message: str) -> str:
        return str(self.unobserved)

    @tcp_server.command(r"U=\d+\.?\d*")
    def set_unobserved(self, message: str) -> str:
        try:
            match = re.search(r"\d+\.?\d*", message)
            if not match:
                return "Could not extract value from command"
            self.unobserved = int(match.group(0))
            return "Unobserved set to {}".format(self.unobserved)
        except ValueError:
            return "Invalid value"
