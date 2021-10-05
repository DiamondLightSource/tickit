from dataclasses import is_dataclass
from typing import Type

import pytest
from immutables import Map
from mock import AsyncMock, MagicMock, create_autospec

from tickit.core.components.component import BaseComponent, Component, ComponentConfig
from tickit.core.state_interfaces.internal import (
    InternalStateConsumer,
    InternalStateProducer,
)
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, Input, Interrupt, Output, SimTime
from tickit.utils.topic_naming import input_topic, output_topic


def test_component_config_is_dataclass():
    assert is_dataclass(ComponentConfig)


def test_component_config_is_config():
    assert isinstance(ComponentConfig, Config)


def test_component_config_configure_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        ComponentConfig.configures()


def test_component_config_kwargs_raises_not_implemented():
    component_config = ComponentConfig(ComponentID("Test"), dict())
    with pytest.raises(NotImplementedError):
        component_config.kwargs


def test_inherit_configurable_component_makes_configurable():
    assert isinstance(
        type("Component", (ConfigurableComponent,), dict()).ComponentConfig, Config
    )


def test_base_component_initialises():
    assert BaseComponent(
        ComponentID("TestBase"),
        MagicMock(InternalStateConsumer),
        MagicMock(InternalStateProducer),
    )


@pytest.fixture
def MockConsumer():
    return create_autospec(InternalStateConsumer, instance=False)


@pytest.fixture
def MockProducer():
    return create_autospec(InternalStateProducer, instance=False)


@pytest.fixture
def TestComponent():
    return type("TestComponent", (BaseComponent,), dict())


@pytest.fixture
def test_component(
    TestComponent: Type[BaseComponent],
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    return TestComponent(
        ComponentID("TestBase"), MockConsumer, MockProducer
    )  # type: ignore


@pytest.mark.asyncio
async def test_base_component_handle_input_awaits_on_tick(
    test_component: BaseComponent,
):
    test_component.on_tick = AsyncMock()  # type: ignore
    await test_component.handle_input(
        Input(ComponentID("Test"), SimTime(42), Changes(Map()))
    )
    test_component.on_tick.assert_awaited_once_with(SimTime(42), Changes(Map()))


@pytest.mark.asyncio
async def test_base_component_output_sends_output(test_component: BaseComponent):
    await test_component.set_up_state_interfaces()
    test_component.state_producer.produce = AsyncMock()  # type: ignore
    await test_component.output(SimTime(42), Changes(Map()), None)
    test_component.state_producer.produce.assert_awaited_once_with(
        output_topic(ComponentID("TestBase")),
        Output(ComponentID("TestBase"), SimTime(42), Changes(Map()), None),
    )


@pytest.mark.asyncio
async def test_base_component_raise_interrupt_sends_output(
    test_component: BaseComponent,
):
    await test_component.set_up_state_interfaces()
    test_component.state_producer.produce = AsyncMock()  # type: ignore
    await test_component.raise_interrupt()
    test_component.state_producer.produce.assert_awaited_once_with(
        output_topic(ComponentID("TestBase")),
        Interrupt(ComponentID("TestBase")),
    )


@pytest.mark.asyncio
async def test_base_component_set_up_state_interfaces_creates_consumer(
    TestComponent: Type[BaseComponent],
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    test_coponent = TestComponent(
        ComponentID("TestBase"), MockConsumer, MockProducer
    )  # type: ignore
    await test_coponent.set_up_state_interfaces()
    assert test_coponent.state_consumer == MockConsumer(AsyncMock())


@pytest.mark.asyncio
async def test_base_component_set_up_state_interfaces_subscribes_consumer(
    test_component: BaseComponent,
):
    await test_component.set_up_state_interfaces()
    test_component.state_consumer.subscribe.assert_called_once_with(  # type: ignore
        [input_topic(ComponentID("TestBase"))]
    )


@pytest.mark.asyncio
async def test_base_component_set_up_state_interfaces_creates_producer(
    TestComponent: Type[BaseComponent],
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    test_component = TestComponent(
        ComponentID("TestBase"), MockConsumer, MockProducer
    )  # type: ignore
    await test_component.set_up_state_interfaces()
    assert test_component.state_producer == MockProducer()


@pytest.mark.asyncio
async def test_base_component_on_tick_raises_not_implemented(
    test_component: BaseComponent,
):
    with pytest.raises(NotImplementedError):
        await test_component.on_tick(SimTime(42), Changes(Map()))


def test_create_simulations_creates_configured(
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    MockComponent = MagicMock(Component, instance=False)
    MockComponentConfig = MagicMock(ComponentConfig, instance=False)
    MockComponentConfig.configures.return_value = MockComponent
    MockComponentConfig.kwargs.return_value = dict()
    config = MockComponentConfig(name=ComponentID("TestComponent"), inputs=dict())

    create_components([config], MockConsumer, MockProducer)
    config.configures().assert_called_once_with(
        name=config.name,
        state_consumer=MockConsumer,
        state_producer=MockProducer,
    )


def test_create_simulations_creates_configured_with_kwargs(
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    MockComponent = MagicMock(Component, instance=False)
    MockComponentConfig = MagicMock(ComponentConfig, instance=False)
    MockComponentConfig.configures.return_value = MockComponent
    MockComponentConfig.kwargs = {"kwarg1": "One", "kwarg2": "Two"}
    config = MockComponentConfig(name=ComponentID("TestComponent"), inputs=dict())

    create_components([config], MockConsumer, MockProducer)
    config.configures().assert_called_once_with(
        name=config.name,
        state_consumer=MockConsumer,
        state_producer=MockProducer,
        **config.kwargs
    )


def test_create_simulations_returns_created_simulations(
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    MockComponent = MagicMock(Component, instance=False)
    MockComponentConfig = MagicMock(ComponentConfig, instance=False)
    MockComponentConfig.configures.return_value = MockComponent
    MockComponentConfig.kwargs.return_value = dict()
    config = MockComponentConfig(name=ComponentID("TestComponent"), inputs=dict())

    assert [config.configures()()] == create_components(
        [config], MockConsumer, MockProducer
    )
