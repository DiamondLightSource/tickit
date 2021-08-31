from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple, Type, Union

from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import (
    Changes,
    ComponentID,
    Input,
    Interrupt,
    IoId,
    Output,
    SimTime,
)
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable
from tickit.utils.configuration.configurable import configurable, configurable_base
from tickit.utils.topic_naming import input_topic, output_topic


@runtime_checkable
class Component(Protocol):
    async def run_forever(self) -> None:
        pass

    async def on_tick(self, time: SimTime, changes: Changes):
        pass


@configurable_base
@dataclass
class ComponentConfig:
    name: ComponentID
    inputs: Dict[IoId, Tuple[ComponentID, IoId]]

    @staticmethod
    def configures() -> Type[Component]:
        raise NotImplementedError

    @property
    def kwargs(self):
        raise NotImplementedError


class ConfigurableComponent:
    def __init_subclass__(cls) -> None:
        cls = configurable(
            ComponentConfig, ignore=["state_consumer", "state_producer"],
        )(cls)


class BaseComponent(ConfigurableComponent):
    def __init__(
        self,
        name: ComponentID,
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
    ) -> None:
        self.name = name
        self._state_consumer_cls = state_consumer
        self._state_producer_cls = state_producer

    async def handle_input(self, input: Input):
        print("{} got {}".format(self.name, input))
        await self.on_tick(input.time, input.changes)

    async def output(
        self, time: SimTime, changes: Changes, call_in: Optional[SimTime],
    ) -> None:
        await self.state_producer.produce(
            output_topic(self.name), Output(self.name, time, changes, call_in)
        )

    async def raise_interrupt(self) -> None:
        await self.state_producer.produce(output_topic(self.name), Interrupt(self.name))

    async def set_up_state_interfaces(self):
        self.state_consumer: StateConsumer[Input] = self._state_consumer_cls(
            self.handle_input
        )
        await self.state_consumer.subscribe([input_topic(self.name)])
        self.state_producer: StateProducer[
            Union[Interrupt, Output]
        ] = self._state_producer_cls()

    @abstractmethod
    async def on_tick(self, time: SimTime, changes: Changes):
        raise NotImplementedError


def create_simulations(
    configs: Iterable[ComponentConfig],
    state_consumer: Type[StateConsumer],
    state_producer: Type[StateProducer],
) -> List[Component]:
    simulations: List[Component] = list()
    for config in configs:
        simulations.append(
            config.configures()(
                name=config.name,
                state_consumer=state_consumer,
                state_producer=state_producer,
                **config.kwargs
            )
        )
    return simulations
