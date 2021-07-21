from typing import Set

from tickit.adapters.interpreters.string_regex import StringRegexInterpreter
from tickit.adapters.servers.tcp import TcpServer
from tickit.core.adapter import ComposedAdapter
from tickit.core.device import UpdateEvent
from tickit.core.typedefs import IoId, SimTime, State


class TcpControlled:
    observed: int = 0
    unobserved: int = 0

    @property
    def outputs(self) -> Set[IoId]:
        return {IoId("observed")}

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        return UpdateEvent(State({IoId("observed"): self.observed}), None)


class TcpControlledAdapter(ComposedAdapter):
    _interpreter = StringRegexInterpreter()
    _server = TcpServer()

    @_interpreter.command(r"O")
    def get_observed(self) -> str:
        return str(self._device.observed)

    @_interpreter.command(r"O=(\d+\.?\d*)", interrupt=True)
    def set_observed(self, value: int) -> str:
        self._device.observed = value
        return "Observed set to {}".format(self._device.observed)

    @_interpreter.command(r"U")
    def get_unobserved(self) -> str:
        return str(self._device.unobserved)

    @_interpreter.command(r"U=(\d+\.?\d*)")
    def set_unobserved(self, value: int) -> str:
        self._device.unobserved = value
        return "Unobserved set to {}".format(self._device.unobserved)
