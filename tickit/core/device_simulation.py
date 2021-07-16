import asyncio
from typing import Optional

from tickit.core.device import Device
from tickit.core.state_interfaces import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, DeviceID, Input, Output, SimTime, State
from tickit.utils.topic_naming import input_topic, output_topic


class DeviceSimulation:

    state: State = State(dict())
    inputs: State = State(dict())

    def __init__(
        self,
        device_id: DeviceID,
        device: Device,
        state_consumer: StateConsumer,
        state_producer: StateProducer,
    ):
        self.device_id = device_id
        self.device = device
        self.last_time: SimTime = SimTime(0)

        self.state_consumer: StateConsumer = state_consumer(
            [input_topic(self.device_id)]
        )
        self.state_producer: StateProducer = state_producer()

    async def run_forever(self):
        for adapter in self.device.adapters:
            asyncio.create_task(adapter.run_forever())
        while True:
            input = await self.state_consumer.consume().__anext__()
            if input:
                await self.on_tick(Input(**input))
            await self.handle_interrupts()
            await asyncio.sleep(0.1)

    async def on_tick(self, input: Input) -> None:
        self.inputs = State({**self.inputs, **State(input.changes)})
        output = self.device.update(SimTime(input.time - self.last_time), self.inputs)
        self.last_time = input.time
        changes = Changes(
            {
                k: v
                for k, v in output.state.items()
                if k not in self.state or not self.state[k] == v
            }
        )
        self.state = output.state
        await self.output(self.last_time, changes, output.call_in)

    async def output(
        self, time: Optional[SimTime], changes: Changes, call_in: Optional[SimTime],
    ) -> None:
        await self.state_producer.produce(
            output_topic(self.device_id), Output(self.device_id, time, changes, call_in)
        )

    async def handle_interrupts(self):
        interrupt = False
        for adapter in self.device.adapters:
            interrupt |= adapter.interrupt
            adapter.interrupt = False
        if interrupt:
            await self.output(None, dict(), 0)
