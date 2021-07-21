import asyncio
from typing import Awaitable, Callable, Iterable, Optional, Type

from tickit.core.adapter import Adapter
from tickit.core.device import Device
from tickit.core.state_interfaces import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, DeviceID, Input, Output, SimTime, State
from tickit.utils.topic_naming import input_topic, output_topic

InterruptHandler = Callable[[], Awaitable[None]]


class DeviceSimulation:

    state: State = State(dict())
    inputs: State = State(dict())

    def __init__(
        self,
        device_id: DeviceID,
        device: Type[Device],
        adapters: Iterable[Callable[[Device, InterruptHandler], Adapter]],
        state_consumer: StateConsumer,
        state_producer: StateProducer,
    ):
        self.device_id = device_id
        self.device = device()
        self.adapters = [
            adapter(self.device, self.handle_interrupt) for adapter in adapters
        ]

        self.state_consumer: StateConsumer[Input] = state_consumer(
            [input_topic(self.device_id)]
        )
        self.state_producer: StateProducer[Output] = state_producer()

    async def run_forever(self):
        for adapter in self.adapters:
            asyncio.create_task(adapter.run_forever())
        while True:
            input = await self.state_consumer.consume().__anext__()
            if input:
                await self.on_tick(Input(**input))
            await asyncio.sleep(0.1)

    async def on_tick(self, input: Input) -> None:
        self.inputs = State({**self.inputs, **State(input.changes)})
        output = self.device.update(SimTime(input.time), self.inputs)
        changes = Changes(
            {
                k: v
                for k, v in output.state.items()
                if k not in self.state or not self.state[k] == v
            }
        )
        self.state = output.state
        await self.output(input.time, changes, output.call_in)

    async def output(
        self, time: Optional[SimTime], changes: Changes, call_in: Optional[SimTime],
    ) -> None:
        await self.state_producer.produce(
            output_topic(self.device_id), Output(self.device_id, time, changes, call_in)
        )

    async def handle_interrupt(self) -> None:
        await self.output(None, Changes(dict()), SimTime(0))
