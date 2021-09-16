from collections import defaultdict

import pytest
from mock import MagicMock

from tickit.core.state_interfaces.internal import (
    InternalStateConsumer,
    InternalStateProducer,
    InternalStateServer,
    Message,
    Messages,
)
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.utils.singleton import Singleton


@pytest.fixture(autouse=True)
def reset_topics():
    InternalStateServer()._topics = defaultdict(lambda: Messages(list()))


@pytest.fixture
def internal_state_server():
    return InternalStateServer()


@pytest.fixture
def internal_state_consumer() -> InternalStateConsumer:
    return InternalStateConsumer(MagicMock())


@pytest.fixture
def internal_state_producer():
    return InternalStateProducer()


@pytest.fixture
def mock_async_callback():
    async def async_callback(value: object) -> None:
        pass

    return MagicMock(async_callback)


def test_internal_state_server_is_singleton():
    assert isinstance(InternalStateServer, Singleton)


def test_internal_state_server_topics_empty(internal_state_server: InternalStateServer):
    assert not internal_state_server._topics


def test_internal_state_server_create_topic_creates_topic(
    internal_state_server: InternalStateServer,
):
    internal_state_server.create_topic("Test")
    assert "Test" in internal_state_server.topics


def test_internal_state_server_remove_topic_removes_topic(
    internal_state_server: InternalStateServer,
):
    internal_state_server.create_topic("Test")
    internal_state_server.remove_topic("Test")
    assert "Test" not in internal_state_server.topics


def test_internal_state_server_create_topic_creates_empty(
    internal_state_server: InternalStateServer,
):
    internal_state_server.create_topic("Test")
    assert list() == internal_state_server._topics["Test"]


@pytest.mark.asyncio
async def test_internal_state_server_push_adds_message(
    internal_state_server: InternalStateServer,
):
    internal_state_server.create_topic("Test")
    await internal_state_server.push("Test", Message("TestMessage"))
    assert Message("TestMessage") in internal_state_server._topics["Test"]


def test_internal_state_consumer_is_state_consumer():
    assert isinstance(InternalStateConsumer, StateConsumer)


@pytest.mark.asyncio
async def test_internal_state_consumer_consumes(
    internal_state_server: InternalStateServer, mock_async_callback: MagicMock
):
    internal_state_consumer = InternalStateConsumer(mock_async_callback)
    await internal_state_consumer.subscribe(["Test"])
    await internal_state_server.push("Test", Message("TestMessage"))
    mock_async_callback.assert_called_once_with("TestMessage")


@pytest.mark.asyncio
async def test_internal_state_consumer_consumes_prior(
    internal_state_server: InternalStateServer, mock_async_callback: MagicMock
):
    internal_state_consumer = InternalStateConsumer(mock_async_callback)
    await internal_state_server.push("Test", Message("TestMessage"))
    await internal_state_consumer.subscribe(["Test"])
    mock_async_callback.assert_called_once_with("TestMessage")


@pytest.mark.asyncio
async def test_internal_state_consumer_consumes_multiple(
    internal_state_server: InternalStateServer, mock_async_callback: MagicMock
):
    internal_state_consumer = InternalStateConsumer(mock_async_callback)
    await internal_state_consumer.subscribe(["Test"])
    await internal_state_server.push("Test", Message("TestMessage"))
    mock_async_callback.assert_called_with("TestMessage")
    await internal_state_server.push("Test", Message("OtherTestMessage"))
    mock_async_callback.assert_called_with("OtherTestMessage")


def test_internal_state_producer_is_state_producer():
    assert isinstance(InternalStateProducer, StateProducer)


@pytest.mark.asyncio
async def test_internal_state_producer_produces(
    internal_state_server: InternalStateServer,
    internal_state_producer: InternalStateProducer,
):
    await internal_state_producer.produce("Test", "TestMessage")
    assert Message("TestMessage") in internal_state_server._topics["Test"]
