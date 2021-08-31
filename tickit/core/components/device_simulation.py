import asyncio
from typing import Awaitable, Callable, Dict, Hashable, List, Type

from immutables import Map

from tickit.core.adapter import AdapterConfig, ListeningAdapter
from tickit.core.components.component import BaseComponent
from tickit.core.device import DeviceConfig
from tickit.core.state_interfaces import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, SimTime, State

InterruptHandler = Callable[[], Awaitable[None]]


class DeviceSimulation(BaseComponent):
    state: State = State(Map())
    device_inputs: Dict[str, Hashable] = dict()

    def __init__(
        self,
        name: ComponentID,
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
        config: DeviceConfig,
        adapters: List[AdapterConfig],
    ):
        super().__init__(name, state_consumer, state_producer)
        self.device = config.configures()(**config.kwargs)
        self.adapters = [
            adapter.configures()(self.device, self.raise_interrupt, **adapter.kwargs)
            for adapter in adapters
        ]

    async def run_forever(self):
        await super().set_up_state_interfaces()
        for adapter in self.adapters:
            asyncio.create_task(adapter.run_forever())

    async def on_tick(self, time: SimTime, changes: Changes) -> None:
        self.device_inputs = {**self.device_inputs, **changes}
        output = self.device.update(SimTime(time), State(Map(self.device_inputs)))
        for adapter in self.adapters:
            if isinstance(adapter, ListeningAdapter):
                adapter.after_update()
        changes = Changes(
            Map(
                {
                    k: v
                    for k, v in output.state.items()
                    if k not in self.state or not self.state[k] == v
                }
            )
        )
        self.state = output.state
        await self.output(time, changes, output.call_in)
