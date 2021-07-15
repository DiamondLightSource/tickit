import asyncio
from typing import Dict, Optional

from tickit.core.device import Device
from tickit.core.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import DeviceID, Input, Output
from tickit.utils.topic_naming import input_topic, output_topic


class DeviceSimulation:

    state = dict()
    inputs = dict()

    def __init__(
        self,
        deviceID: DeviceID,
        device: Device,
        state_consumer: StateConsumer,
        state_producer: StateProducer,
    ):
        self.deviceID = deviceID
        self.device = device
        self.last_time = 0

        self.state_consumer: StateConsumer = state_consumer(
            [input_topic(self.deviceID)]
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
        self.inputs = {**self.inputs, **input.changes}
        new_state, call_in = self.device.update(
            input.time - self.last_time, self.inputs
        )
        self.last_time = input.time
        changes = {
            k: v
            for k, v in new_state.items()
            if k not in self.state or not self.state[k] == v
        }
        self.state = new_state
        await self.output(self.last_time, changes, call_in)

    async def output(
        self, time: Optional[int], changes: Dict[str, object], call_in: int
    ):
        await self.state_producer.produce(
            output_topic(self.deviceID), Output(self.deviceID, time, changes, call_in)
        )

    async def handle_interrupts(self):
        interrupt = False
        for adapter in self.device.adapters:
            interrupt |= adapter.interrupt
            adapter.interrupt = False
        if interrupt:
            await self.output(None, dict(), 0)
