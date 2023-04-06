from dataclasses import is_dataclass
from typing import Type

import pytest
from immutables import Map
from mock import AsyncMock, create_autospec

from tickit.core.components.component import BaseComponent, ComponentConfig
from tickit.core.state_interfaces.internal import (
    InternalStateConsumer,
    InternalStateProducer,
)
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, Input, Interrupt, Output, SimTime
from tickit.utils.topic_naming import input_topic, output_topic


def test_component_config_is_dataclass():
    assert is_dataclass(ComponentConfig)


def test_base_component_initialises():
    assert BaseComponent(ComponentID("TestBase"))


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
def test_component(TestComponent: Type[BaseComponent]):
    return TestComponent(ComponentID("TestBase"))  # type: ignore


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
async def test_base_component_output_sends_output(
    test_component: BaseComponent,
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    await test_component.run_forever(MockConsumer, MockProducer)
    test_component.state_producer.produce = AsyncMock()  # type: ignore
    await test_component.output(SimTime(42), Changes(Map()), None)
    test_component.state_producer.produce.assert_awaited_once_with(
        output_topic(ComponentID("TestBase")),
        Output(ComponentID("TestBase"), SimTime(42), Changes(Map()), None),
    )


@pytest.mark.asyncio
async def test_base_component_raise_interrupt_sends_output(
    test_component: BaseComponent,
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    await test_component.run_forever(MockConsumer, MockProducer)
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
    test_component = TestComponent(ComponentID("TestBase"))  # type: ignore
    await test_component.run_forever(MockConsumer, MockProducer)
    assert test_component.state_consumer == MockConsumer(AsyncMock())


@pytest.mark.asyncio
async def test_base_component_set_up_state_interfaces_subscribes_consumer(
    test_component: BaseComponent,
    MockConsumer: Type[StateConsumer],
    MockProducer: Type[StateProducer],
):
    await test_component.run_forever(MockConsumer, MockProducer)
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
        ComponentID("TestBase"),
    )  # type: ignore
    await test_component.run_forever(MockConsumer, MockProducer)
    assert test_component.state_producer == MockProducer()


@pytest.mark.asyncio
async def test_base_component_on_tick_raises_not_implemented(
    test_component: BaseComponent,
):
    with pytest.raises(NotImplementedError):
        await test_component.on_tick(SimTime(42), Changes(Map()))
