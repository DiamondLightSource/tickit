import logging
from typing import Any, Dict, Generic, List, Tuple, TypedDict, TypeVar

import pydantic.v1.dataclasses
from typing_extensions import NotRequired

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime

LOGGER = logging.getLogger(__name__)

A = TypeVar("A")
V = TypeVar("V")


class IoBoxDevice(Device, Generic[A, V]):
    """
    A simple device which can take and store key-value pairs from both
    network adapters and the ticket graph.

    Adapters should write values to the device via device.write(addr, value)
    or device[addr] = value. The writes will be pending until the scheduler
    interrupts the device. For example:

    ```python
    device[foo]
    >> 5
    device[foo] = 6
    device[foo]
    >> 5
    interrupt()
    device[foo]
    >> 6
    ```

    Linked devices can send values to be written via inputs and receive changes
    via outputs. For example:
    ```python
    update = box.update(SimTime(0), {"updates": [(4, "foo")]})
    assert update.outputs["updates"] == [(4, "foo")]
    >> 6
    ```

    The two modes of I/O may used independently, optionally and interoperably.

    This device is useful for simulating a basic block of memory.
    The envisioned use of this class is where you wish to simulate a network
    interface but the internal hardware logic is either not needed or very simple.
    A custom adapter can be made for the network interface and can simply
    read and write to an IoBox.
    """

    #: A typed mapping containing the 'input' input value
    Inputs: TypedDict = TypedDict(
        "Inputs", {"updates": NotRequired[List[Tuple[Any, Any]]]}
    )
    #: An empty typed mapping of device outputs
    Outputs: TypedDict = TypedDict(
        "Outputs", {"updates": NotRequired[List[Tuple[Any, Any]]]}
    )

    _memory: Dict[A, V]
    _change_buffer: List[Tuple[A, V]]

    def __init__(self) -> None:  # noqa: D107
        self._memory = {}
        self._change_buffer = []

    def write(self, addr: A, value: V) -> None:
        """Write a value to an address.

        The value will only make it into memory when update() is called
        e.g. by an interrupt.

        Args:
            addr (A): Address to store value
            value (V): Value to store
        """
        self._change_buffer.append((addr, value))

    def read(self, addr: A) -> V:
        """Read a value from an address.

        Args:
            addr (A): Address to find value

        Returns:
            V: Value at address

        Raises:
            ValueError: If no value stored at address
        """
        return self._memory[addr]

    # As well as read and write, can use device[addr] and device[addr] = "foo"
    __getitem__ = read
    __setitem__ = write

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """Write all pending values to their addresses.

        Args:
            time (SimTime): (Simulated) time at which this is called
            inputs (Inputs): Inputs to this device, may contain addresses
                and values to update

        Returns:
            DeviceUpdate[Outputs]: Outputs and update, may contain addresses
                and values that have been updated, either via inputs or
                an adapter
        """
        self._change_buffer += inputs.get("updates", [])
        updates = []
        while self._change_buffer:
            addr, value = self._change_buffer.pop()
            self._memory[addr] = value
            updates.append((addr, value))
        return DeviceUpdate(IoBoxDevice.Outputs(updates=updates), None)


@pydantic.v1.dataclasses.dataclass
class IoBox(ComponentConfig):
    """Arbitrary box of key-value pairs."""

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=IoBoxDevice(),
        )
