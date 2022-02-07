import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Type, Union

from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import (
    Changes,
    ComponentID,
    ComponentPort,
    Input,
    Interrupt,
    Output,
    PortID,
    SimTime,
)
from tickit.utils.configuration.configurable import as_tagged_union
from tickit.utils.topic_naming import input_topic, output_topic

LOGGER = logging.getLogger(__name__)


@dataclass  # type: ignore
@as_tagged_union
class Component:
    """An interface for types which implement stand-alone simulation components.

    An interface for types which implement stand-alone simulation components.
    Components define the top level building blocks of a tickit simulation (examples
    include the DeviceSimulation which host a device and corresponding adapter or a
    SystemSimulation which hosts a SlaveScheduler and internal Components).
    """

    name: ComponentID

    @abstractmethod
    async def run_forever(
        self, state_consumer: Type[StateConsumer], state_producer: Type[StateProducer]
    ) -> None:
        """An asynchronous method allowing indefinite running of core logic."""

    @abstractmethod
    async def on_tick(self, time: SimTime, changes: Changes):
        """An asynchronous method called whenever the component is to be updated.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """


@dataclass  # type: ignore
@as_tagged_union
class ComponentConfig:
    """A data container for component configuration.

    A data container for component configuration which acts as a named union of
    subclasses to facilitate automatic deserialization.
    """

    name: ComponentID
    inputs: Dict[PortID, ComponentPort]

    @abstractmethod
    def __call__(self) -> Component:
        """Create the component from the given config."""
        raise NotImplementedError(self)


class BaseComponent(Component):
    """A base class for compnents, implementing state interface related methods."""

    state_consumer: StateConsumer[Input]
    state_producer: StateProducer[Union[Interrupt, Output]]

    async def handle_input(self, input: Input):
        """Calls on_tick when an input is recieved.

        Args:
            input (Input): An immutable data container for Component inputs.
        """
        LOGGER.debug("{} got {}".format(self.name, input))
        await self.on_tick(input.time, input.changes)

    async def output(
        self,
        time: SimTime,
        changes: Changes,
        call_at: Optional[SimTime],
    ) -> None:
        """Constructs and sends an Output message to the component output topic.

        An asynchronous method which constructs an Output message tagged with the
        component name and sends it to the output topic of this component.

        Args:
            time (SimTime): The current time (in nanoseconds).
            changes (Changes): A mapping of the difference between the last observable
                state and the current observable state.
            call_at (Optional[SimTime]): The simulation time at which the component
                requests to be awoken.
        """
        await self.state_producer.produce(
            output_topic(self.name), Output(self.name, time, changes, call_at)
        )

    async def raise_interrupt(self) -> None:
        """Sends an Interrupt message to the component output topic.

        An asynchronous method whicb constructs an Interrupt message tagged with the
        component name and sends it to the output topic of this component.
        """
        await self.state_producer.produce(output_topic(self.name), Interrupt(self.name))

    async def run_forever(
        self, state_consumer: Type[StateConsumer], state_producer: Type[StateProducer]
    ) -> None:
        """Creates and configures a state consumer and state producer.

        An asynchronous method which creates a state consumer which is subscribed to
        the input topic of the component and calls back to handle_input, and a state
        producer to produce Interrupt or Output messages.
        """
        self.state_consumer = state_consumer(self.handle_input)
        await self.state_consumer.subscribe([input_topic(self.name)])
        self.state_producer = state_producer()

    @abstractmethod
    async def on_tick(self, time: SimTime, changes: Changes):
        """An abstract asynchronous method which implements the core logic of the component.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """
        raise NotImplementedError
