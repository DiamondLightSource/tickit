import pytest

from tickit.core.state_interfaces import state_interface
from tickit.core.state_interfaces.state_interface import (
    StateConsumer,
    StateProducer,
    add,
    get_interface,
    interfaces,
)


@pytest.fixture(autouse=True)
def reset_consumers():
    old_consumers = state_interface.consumers
    state_interface.consumers = dict()
    yield
    state_interface.consumers = old_consumers


@pytest.fixture(autouse=True)
def reset_producers():
    old_producers = state_interface.producers
    state_interface.producers = dict()
    yield
    state_interface.producers = old_producers


@pytest.fixture
def TestStateConsumer():
    return type("TestStateConsumer", (StateConsumer,), dict())


@pytest.fixture
def TestStateProducer():
    return type("TestStateProducer", (StateProducer,), dict())


def test_test_interface_not_in_interfaces():
    assert set() == interfaces()


def test_add_only_consumer_not_in_interfaces(TestStateConsumer):
    add("Test", False)(TestStateConsumer)
    assert "Test" not in interfaces()


def test_add_only_producer_not_in_interfaces(TestStateProducer):
    add("Test", False)(TestStateProducer)
    assert "Test" not in interfaces()


def test_add_both_adds_to_interfaces(TestStateConsumer, TestStateProducer):
    add("Test", False)(TestStateConsumer)
    add("Test", False)(TestStateProducer)
    assert "Test" in interfaces()


def test_add_non_interface_warns():
    with pytest.warns(RuntimeWarning):
        add("Test", False)(type("TestClass", tuple(), dict()))


def test_get_returns_consumer(TestStateConsumer, TestStateProducer):
    add("Test", False)(TestStateConsumer)
    add("Test", False)(TestStateProducer)
    consumer, _ = get_interface("Test")
    assert consumer == TestStateConsumer


def test_get_returns_producer(TestStateConsumer, TestStateProducer):
    add("Test", False)(TestStateConsumer)
    add("Test", False)(TestStateProducer)
    _, producer = get_interface("Test")
    assert producer == TestStateProducer
