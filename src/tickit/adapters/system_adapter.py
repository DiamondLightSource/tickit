from typing import Dict, Union

from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
from tickit.adapters.interpreters.command.regex_command import RegexCommand
from tickit.core.components.component import BaseComponent, Component
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.typedefs import ComponentID
from tickit.utils.byte_format import ByteFormat


class BaseSystemSimulationAdapter:
    """A common base adapter for system simulation adapters.

    They should be able to use any interpreter available.
    """

    _components: Dict[ComponentID, Component]
    _wiring: Union[Wiring, InverseWiring]

    def setup_adapter(
        self,
        components: Dict[ComponentID, Component],
        wiring: Union[Wiring, InverseWiring],
    ) -> None:
        self._components = components
        self._wiring = wiring


class SystemSimulationAdapter(BaseSystemSimulationAdapter, CommandInterpreter):
    """Network adapter for a generic system simulation.

    Network adapter for a generic system simulation using a command interpreter. This
    Can be used to query the system simulation component for a list of the
    ComponentID's for the components in the system and given a specific ID, the details
    of that component.
    """

    _byte_format: ByteFormat = ByteFormat(b"%b\r\n")

    @RegexCommand(r"ids", False, "utf-8")
    async def get_component_ids(self) -> bytes:
        """Returns a list of ids for all the components in the system simulation."""
        return str(self._components.keys()).encode("utf-8")

    @RegexCommand(r"id=(\w+)", False, "utf-8")
    async def get_component_info(self, id: str) -> bytes:
        """Returns the component info of the given id."""
        component = self._components.get(ComponentID(id), "ComponentID not recognised.")

        if isinstance(component, DeviceSimulation):
            return str(
                f"ComponentID: {component.name}\n"
                + f" device: {component.device.__class__.__name__}\n"
                + " adapters: "
                + f"{[adapter.__class__.__name__ for adapter in component.adapters]}\n"
                + f" Inputs: {component.device_inputs}\n"
                + f" last_outputs: {component.last_outputs}\n"
            ).encode("utf-8")
        else:
            return str(component).encode("utf-8")

    @RegexCommand(r"wiring", False, "utf-8")
    async def get_wiring(self) -> bytes:
        """Returns the wiring object used by the nested scheduler."""
        return str(self._wiring).encode("utf-8")

    @RegexCommand(r"interrupt=(\w+)", False, "utf-8")
    async def raise_component_interrupt(self, id: str) -> bytes:
        """Returns the component info of the given id."""
        component = self._components.get(ComponentID(id), None)

        if isinstance(component, BaseComponent):
            await component.raise_interrupt()
            return str(f"Raised Interupt in {component.name}").encode("utf-8")
        else:
            return str("ComponentID not recognised, No interupt raised.").encode(
                "utf-8"
            )
