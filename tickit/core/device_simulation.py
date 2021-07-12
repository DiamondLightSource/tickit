import asyncio

from tickit.core.device import Device
from tickit.core.events import DeviceID, Input, Output
from tickit.core.state_interface import StateConsumer, StateProducer
from tickit.utils.topic_naming import input_topic, output_topic


class DeviceSimulation:

    # TODO add the device interface
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
        self.state, call_in = self.device.initial_state
        await self.state_producer.produce(
            output_topic(self.deviceID),
            Output(self.deviceID, None, self.state, call_in),
        )

        while True:
            input = await self.state_consumer.consume().__anext__()
            if input:
                await self.on_tick(Input(**input))
            await asyncio.sleep(0.1)

    async def on_tick(self, input: Input) -> None:
        self.inputs |= input.changes
        new_state, call_in = self.device.update(
            input.time - self.last_time, self.inputs
        )
        self.last_time = input.time
        changes = {k: v for k, v in new_state.items() if not self.state[k] == v}
        self.state = new_state
        await self.state_producer.produce(
            output_topic(self.deviceID),
            Output(self.deviceID, self.last_time, changes, call_in),
        )
