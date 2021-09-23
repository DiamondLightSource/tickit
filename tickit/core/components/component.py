import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Type, Union

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
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable
from tickit.utils.configuration.configurable import configurable, configurable_base
from tickit.utils.topic_naming import input_topic, output_topic

LOGGER = logging.getLogger(__name__)


@runtime_checkable
class Component(Protocol):
    """An interface for types which implement stand-alone simulation components.

    An interface for types which implement stand-alone simulation components.
    Components define the top level building blocks of a tickit simulation (examples
    include the DeviceSimulation which host a device and corresponding adapter or a
    SystemSimulation which hosts a SlaveScheduler and internal Components).
    """

    async def run_forever(self) -> None:
        """An asynchronous method allowing indefinite running of core logic."""
        pass

    async def on_tick(self, time: SimTime, changes: Changes):
        """An asynchronous method called whenever the component is to be updated.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """
        pass


@configurable_base
@dataclass
class ComponentConfig:
    """A data container for component configuration.

    A data container for component configuration which acts as a named union of
    subclasses to facilitate automatic deserialization.
    """

    name: ComponentID
    inputs: Dict[PortID, ComponentPort]

    @staticmethod
    def configures() -> Type[Component]:
        """The Component class configured by this config type.

        Returns:
            Type[Component]: The Component class configured by this config type.
        """
        raise NotImplementedError

    @property
    def kwargs(self) -> Dict[str, object]:
        """The key word arguments of the configured component.

        Returns:
            Dict[str, object]: The key word argument of the configured Component.
        """
        raise NotImplementedError


class ConfigurableComponent:
    """A mixin used to create a component with a configuration data container."""

    def __init_subclass__(cls) -> None:
        """A subclass init method which makes the subclass configurable.

        A subclass init method which makes the subclass configurable with a
        ComponentConfig template, ignoring the "state_consumer" and "state_producer"
        arguments.
        """
        cls = configurable(
            ComponentConfig,
            ignore=["state_consumer", "state_producer"],
        )(cls)


class BaseComponent(ConfigurableComponent):
    """A base class for compnents, implementing state interface related methods."""

    def __init__(
        self,
        name: ComponentID,
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
    ) -> None:
        """A BaseComponent constructor which stores state interface types.

        Args:
            name (ComponentID): The unique identifier of the component.
            state_consumer (Type[StateConsumer]): The state consumer class to be used
                by the component.
            state_producer (Type[StateProducer]): The state producer class to be used
                by the component.
        """
        self.name = name
        self._state_consumer_cls = state_consumer
        self._state_producer_cls = state_producer

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

    async def set_up_state_interfaces(self):
        """Creates and configures a state consumer and state producer.

        An asynchronous method which creates a state consumer which is subscribed to
        the input topic of the component and calls back to handle_input, and a state
        producer to produce Interrupt or Output messages.
        """
        self.state_consumer: StateConsumer[Input] = self._state_consumer_cls(
            self.handle_input
        )
        await self.state_consumer.subscribe([input_topic(self.name)])
        self.state_producer: StateProducer[
            Union[Interrupt, Output]
        ] = self._state_producer_cls()

    @abstractmethod
    async def on_tick(self, time: SimTime, changes: Changes):
        """An abstract asynchronous method which implements the core logic of the component.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """
        raise NotImplementedError


def create_components(
    configs: Iterable[ComponentConfig],
    state_consumer: Type[StateConsumer],
    state_producer: Type[StateProducer],
) -> List[Component]:
    """Creates a list of components from component config objects.

    Args:
        configs (Iterable[ComponentConfig]): An iterable of component configuration
            data containers.
        state_consumer (Type[StateConsumer]): The state consumer class to be used by
            the components.
        state_producer (Type[StateProducer]): The state producer class to be used by
            the components.

    Returns:
        List[Component]: A list of instantiated components.
    """
    components: List[Component] = list()
    for config in configs:
        components.append(
            config.configures()(
                name=config.name,
                state_consumer=state_consumer,
                state_producer=state_producer,
                **config.kwargs
            )
        )
    return components
