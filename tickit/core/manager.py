import asyncio
import bisect
from time import time_ns
from typing import List, Optional, Set, Tuple

from tickit.core.event_router import EventRouter, Wiring
from tickit.core.state_interface import StateConsumer, StateProducer, StateTopicManager
from tickit.core.typedefs import DeviceID, Input, Output, Wakeup
from tickit.utils.topic_naming import input_topic, output_topic


class Manager:
    def __init__(
        self,
        wiring: Wiring,
        state_consumer: StateConsumer,
        state_producer: StateProducer,
        state_topic_manager: StateTopicManager,
        initial_time: int = 0,
        simulation_speed: float = 1.0,
    ):
        self.event_router = EventRouter(wiring)
        self.simulation_time = initial_time
        self.simulation_speed = simulation_speed

        self.state_topic_manager = state_topic_manager()
        output_topics, _ = self.create_device_topics()

        self.state_consumer: StateConsumer = state_consumer(output_topics)
        self.state_producer: StateProducer = state_producer()
        self.wakeups: List[Wakeup] = []

    def create_device_topics(self) -> Tuple[Set[str], Set[str]]:
        output_topics = set(
            output_topic(device) for device in self.event_router.devices
        )
        input_topics = set(input_topic(device) for device in self.event_router.devices)
        for topic in set.union(input_topics, output_topics):
            self.state_topic_manager.create_topic(topic)
        return output_topics, input_topics

    async def run_forever(self):
        time = time_ns()
        while True:
            last_time = time
            if self.wakeups and self.wakeups[0].when == self.simulation_time:
                await self.tick()
            await self.handle_callbacks()
            await asyncio.sleep(0.1)
            time = time_ns()
            self.progress(time - last_time)

    def progress(self, wall_time: int):
        new_time = self.simulation_time + wall_time * self.simulation_speed
        if self.wakeups:
            new_time = min(new_time, self.wakeups[0].when)
        self.simulation_time = new_time
        print("Progressed to {}".format(self.simulation_time))

    async def tick(self) -> None:
        print("Doing tick @ {}".format(self.simulation_time))
        assert self.simulation_time == self.wakeups[0].when
        wakeup = self.wakeups.pop(0)
        to_update = self.event_router.dependants(wakeup.device)
        inputs: List[Input] = list()

        await self.state_producer.produce(
            input_topic(wakeup.device), Input(wakeup.device, self.simulation_time, {})
        )
        while to_update:
            response: Output = await self.handle_callbacks()
            if not response or not response.time:
                await asyncio.sleep(0.1)
                continue
            assert response.time == self.simulation_time
            to_update.discard(response.source)
            inputs.extend(self.event_router.route(response))
            tasks = [
                asyncio.create_task(
                    self.update_device(self.collate_inputs(inputs, device))
                )
                for device in to_update
                if not self.event_router.inverse_device_tree[device].intersection(
                    to_update
                )
            ]
            if tasks:
                await asyncio.wait(tasks)

    def collate_inputs(self, inputs: List[Input], device: DeviceID) -> Input:
        inputs = [input for input in inputs if input.target == device]
        return Input(
            inputs[0].target,
            inputs[0].time,
            {k: v for input in inputs for k, v in input.changes.items()},
        )

    async def update_device(self, input: Input) -> None:
        await self.state_producer.produce(input_topic(input.target), input)

    async def handle_callbacks(self) -> Optional[Output]:
        output = await self.state_consumer.consume().__anext__()
        if not output:
            return None
        output = Output(**output)
        if output.call_in is not None:
            wakeup = Wakeup(output.source, self.simulation_time + output.call_in)
            print("Scheduling wakeup {}".format(wakeup))
            self.wakeups.insert(bisect.bisect(self.wakeups, wakeup), wakeup)
        return output
