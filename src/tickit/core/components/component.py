import asyncio
import logging
import traceback
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Type

import pydantic.v1.dataclasses

from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import (
    Changes,
    ComponentException,
    ComponentID,
    ComponentInput,
    ComponentOutput,
    ComponentPort,
    Input,
    Interrupt,
    Output,
    PortID,
    SimTime,
    StopComponent,
)
from tickit.utils.configuration.tagged_union import as_tagged_union
from tickit.utils.topic_naming import input_topic, output_topic

LOGGER = logging.getLogger(__name__)


@dataclass
class Component:
    """An interface for types which implement stand-alone simulation components.

    An interface for types which implement stand-alone simulation components.
    Components define the top level building blocks of a tickit simulation (examples
    include the DeviceComponent which host a device and corresponding adapter or a
    SystemComponent which hosts a NestedScheduler and internal Components).
    """

    name: ComponentID

    @abstractmethod
    async def run_forever(
        self, state_consumer: Type[StateConsumer], state_producer: Type[StateProducer]
    ) -> None:
        """Asynchronous method allowing indefinite running of core logic."""

    @abstractmethod
    async def on_tick(self, time: SimTime, changes: Changes):
        """Asynchronous method called whenever the component is to be updated.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """


@as_tagged_union
@pydantic.v1.dataclasses.dataclass
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
    """A base class for components, implementing state interface related methods."""

    state_consumer: StateConsumer[ComponentInput]
    state_producer: StateProducer[ComponentOutput]

    async def handle_input(self, message: ComponentInput):
        """Call on_tick when an input is received.

        Args:
            message (ComponentInput): An immutable data container for any
                message a component receives.
        """
        if isinstance(message, Input):
            LOGGER.debug(f"{self.name} got {message}")
            try:
                await asyncio.gather(
                    self.on_tick(message.time, message.changes), return_exceptions=False
                )
            except Exception as err:
                LOGGER.exception(f"Exception occurred in {self.name} component.")
                await self.state_producer.produce(
                    output_topic(self.name),
                    ComponentException(self.name, err, traceback.format_exc()),
                )
        if isinstance(message, StopComponent):
            await self.stop_component()

    async def output(
        self,
        time: SimTime,
        changes: Changes,
        call_at: Optional[SimTime],
    ) -> None:
        """Construct and send an Output message to the component output topic.

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

        An asynchronous method which constructs an Interrupt message tagged with the
        component name and sends it to the output topic of this component.
        """
        await self.state_producer.produce(output_topic(self.name), Interrupt(self.name))

    async def run_forever(
        self, state_consumer: Type[StateConsumer], state_producer: Type[StateProducer]
    ) -> None:
        """Creates and configures a state consumer and state producer.

        An asynchronous method which creates a state consumer which is subscribed to
        the input topic of the component and calls back to handle_input, and a state
        producer to produce Interrupt, Output or ComponentException messages.
        """
        self.state_consumer = state_consumer(self.handle_input)
        await self.state_consumer.subscribe([input_topic(self.name)])
        self.state_producer = state_producer()

    @abstractmethod
    async def on_tick(self, time: SimTime, changes: Changes):
        """Abstract asynchronous method which implements core logic of the component.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """
        raise NotImplementedError

    @abstractmethod
    async def stop_component(self) -> None:
        """Abstract asynchronous method which cancels the running component tasks."""
        raise NotImplementedError
