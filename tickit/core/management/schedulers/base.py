from abc import abstractmethod
from typing import Type, Union

from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.ticker import Ticker
from tickit.core.state_interfaces import StateConsumer, StateProducer
from tickit.core.typedefs import ComponentID, Input, Interrupt, Output, SimTime, Wakeup
from tickit.utils.priority_queue import ManyAsyncPriorityQueue
from tickit.utils.topic_naming import input_topic, output_topic


class BaseScheduler:
    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
    ) -> None:
        self._wiring = wiring
        self._state_consumer_cls = state_consumer
        self._state_producer_cls = state_producer

    async def schedule_wakeup(
        self, source: ComponentID, time: SimTime, call_in: SimTime
    ) -> None:
        await self.add_wakeup(source, SimTime(time + call_in))

    @abstractmethod
    async def schedule_interrupt(self, source: ComponentID) -> None:
        raise NotImplementedError

    async def update_component(self, input: Input) -> None:
        await self.state_producer.produce(input_topic(input.target), input)

    async def handle_message(self, message: Union[Interrupt, Output]) -> None:
        print("Scheduler got {}".format(message))
        if isinstance(message, Output):
            await self.ticker.propagate(message)
            if message.call_in is not None:
                await self.schedule_wakeup(
                    message.source, message.time, message.call_in
                )
        if isinstance(message, Interrupt):
            await self.schedule_interrupt(message.source)

    async def setup(self) -> None:
        self.ticker = Ticker(self._wiring, self.update_component)
        self.state_consumer: StateConsumer[
            Union[Interrupt, Output]
        ] = self._state_consumer_cls(self.handle_message)
        await self.state_consumer.subscribe(
            {output_topic(component) for component in self.ticker.components}
        )
        self.state_producer: StateProducer[Input] = self._state_producer_cls()
        self.wakeups: ManyAsyncPriorityQueue[Wakeup] = ManyAsyncPriorityQueue()

    async def add_wakeup(self, component: ComponentID, when: SimTime) -> None:
        wakeup = Wakeup(component, when)
        print("Scheduling {}".format(wakeup))
        await self.wakeups.put((wakeup.when, wakeup))
