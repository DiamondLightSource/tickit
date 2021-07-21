from typing import Set

from tickit.core.device import UpdateEvent
from tickit.core.typedefs import IoId, SimTime, State


class Sink:
    @property
    def outputs(self) -> Set[IoId]:
        return set()

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        print("Sunk {}".format(inputs))
        return UpdateEvent(State(dict()), None)
