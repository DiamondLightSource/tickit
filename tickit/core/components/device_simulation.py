import asyncio
from typing import Awaitable, Callable, Dict, Hashable, List, Mapping, Type, cast

from immutables import Map

from tickit.core.adapter import AdapterConfig, ListeningAdapter
from tickit.core.components.component import BaseComponent
from tickit.core.device import DeviceConfig, DeviceUpdate
from tickit.core.lifetime_runnable import run_all
from tickit.core.state_interfaces import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, SimTime, State

InterruptHandler = Callable[[], Awaitable[None]]


class DeviceSimulation(BaseComponent):
    """A component containing a device and the corresponding adapters.

    A component which thinly wraps a device and the corresponding adapters, this
    component delegates core behaviour to the update method of the device, whilst
    allowing adapters to raise interrupts.
    """

    last_outputs: State = State(dict())
    device_inputs: Dict[str, Hashable] = dict()

    def __init__(
        self,
        name: ComponentID,
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
        device: DeviceConfig,
        adapters: List[AdapterConfig],
    ):
        """A DeviceSimulation constructor which builds a device and adapters from config.

        Args:
            name (ComponentID):  The unique identifier of the device simulation.
            state_consumer (Type[StateConsumer]): The state consumer class to be used
                by the component.
            state_producer (Type[StateProducer]): The state producer class to be used
                by the component.
            device (DeviceConfig): An immuatable device configuration data container,
                used to construct the device.
            adapters (List[AdapterConfig]): A list of immutable adapter configuration
                data containers, used to construct adapters.
        """
        super().__init__(name, state_consumer, state_producer)
        self.device = device.configures()(**device.kwargs)
        self.adapters = [
            adapter.configures()(self.device, self.raise_interrupt, **adapter.kwargs)
            for adapter in adapters
        ]

    async def run_forever(self):
        """Sets up state interfaces, runs adapters and blocks until any complete."""
        tasks = run_all(self.adapters)
        await self.set_up_state_interfaces()
        if tasks:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    async def on_tick(self, time: SimTime, changes: Changes) -> None:
        """Delegates core behaviour to the device and calls adapter on_update.

        An asynchronous method which updates device inputs according to external
        changes, delegates core behaviour to the device update method, informs
        ListeningAdapters of the update, computes changes to the state of the component
        and sends the resulting Output.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """
        self.device_inputs = {
            **self.device_inputs,
            **cast(Mapping[str, Hashable], changes),
        }
        device_update: DeviceUpdate = self.device.update(
            SimTime(time), self.device_inputs
        )
        for adapter in self.adapters:
            if isinstance(adapter, ListeningAdapter):
                adapter.after_update()
        out_changes = Changes(
            Map(
                {
                    k: v
                    for k, v in device_update.outputs.items()
                    if k not in self.last_outputs or not self.last_outputs[k] == v
                }
            )
        )
        self.last_outputs = device_update.outputs
        await self.output(time, out_changes, device_update.call_at)
