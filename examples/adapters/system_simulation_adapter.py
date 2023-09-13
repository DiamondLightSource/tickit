from tickit.adapters.specifications import RegexCommand
from tickit.adapters.system import BaseSystemSimulationAdapter
from tickit.adapters.tcp import CommandAdapter
from tickit.core.components.component import BaseComponent
from tickit.core.components.device_component import DeviceComponent
from tickit.core.typedefs import ComponentID
from tickit.utils.byte_format import ByteFormat


class SystemSimulationAdapter(BaseSystemSimulationAdapter, CommandAdapter):
    """Network adapter for a generic system simulation.

    Network adapter for a generic system simulation using a CommandAdapter. This
    Can be used to query the SystemComponent for a list of ID's of the
    components it contains; to provide the details of a component given its ID; and
    to return the wiring map of the components.
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

        if isinstance(component, DeviceComponent):
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
        """Raises an interrupt in the component of the given id."""
        component = self._components.get(ComponentID(id), None)

        if isinstance(component, BaseComponent):
            await component.raise_interrupt()
            return str(f"Raised Interupt in {component.name}").encode("utf-8")
        else:
            return str("ComponentID not recognised, No interupt raised.").encode(
                "utf-8"
            )
