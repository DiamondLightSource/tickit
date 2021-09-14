import logging
from abc import abstractmethod
from typing import Type, Union

from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.ticker import Ticker
from tickit.core.state_interfaces import StateConsumer, StateProducer
from tickit.core.typedefs import ComponentID, Input, Interrupt, Output, SimTime, Wakeup
from tickit.utils.priority_queue import ManyAsyncPriorityQueue
from tickit.utils.topic_naming import input_topic, output_topic

LOGGER = logging.getLogger(__name__)


class BaseScheduler:
    """A base scheduler class which implements logic common to all schedulers"""

    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
    ) -> None:
        """A constructor which stores wiring and state interface classes for reference

        Args:
            wiring (Union[Wiring, InverseWiring]): A wiring or inverse wiring object
                representing the connections between components in the system
            state_consumer (Type[StateConsumer]): The state consumer class to be used
                by the component
            state_producer (Type[StateProducer]): The state producer class to be used
                by the component
        """
        self._wiring = wiring
        self._state_consumer_cls = state_consumer
        self._state_producer_cls = state_producer

    async def schedule_wakeup(
        self, source: ComponentID, time: SimTime, call_in: SimTime
    ) -> None:
        """A asynchronous method which schedules a wakeup at time + call_in

        Args:
            source (ComponentID): The component which should be updated
            time (SimTime): The time at which the wakeup is requested
            call_in (SimTime): The time in which the wakeup should occur
        """
        await self.add_wakeup(source, SimTime(time + call_in))

    @abstractmethod
    async def schedule_interrupt(self, source: ComponentID) -> None:
        """An abstract asynchronous method which should schedule an interrupt immediately

        Args:
            source (ComponentID): The component which should be updated
        """
        raise NotImplementedError

    async def update_component(self, input: Input) -> None:
        """An asynchronous method which sends an input to the input topic of a component

        Args:
            input (Input): The input message to be sent to the component
        """
        await self.state_producer.produce(input_topic(input.target), input)

    async def handle_message(self, message: Union[Interrupt, Output]) -> None:
        """An asynchronous method which handles messages produced by the state consumer

        An asynchronous method which handles interrupt and output messages produced by
        the state consumer; For Outputs, changes are propagated and wakeups scheduled
        if required, whilst handling of interrupts is deferred

        Args:
            message (Union[Interrupt, Output]): An Interrupt or Output produced by the
                state consumer
        """
        LOGGER.debug("Scheduler got {}".format(message))
        if isinstance(message, Output):
            await self.ticker.propagate(message)
            if message.call_in is not None:
                await self.schedule_wakeup(
                    message.source, message.time, message.call_in
                )
        if isinstance(message, Interrupt):
            await self.schedule_interrupt(message.source)

    async def setup(self) -> None:
        """An asynchronous method which initializes asynchronous components of the scheduler

        An asynchronous setup method which creates a ticker, a state consumer which is
        subscribed to the output topics of each component in the system, a state
        producer to produce component inputs, and initializes the async priority queue
        """
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
        """An asynchronous method which adds a wakeup to the priority queue

        Args:
            component (ComponentID): The component which should be updated
            when (SimTime): The simulation time at which the update should occur
        """
        wakeup = Wakeup(component, when)
        LOGGER.debug("Scheduling {}".format(wakeup))
        await self.wakeups.put((wakeup.when, wakeup))
