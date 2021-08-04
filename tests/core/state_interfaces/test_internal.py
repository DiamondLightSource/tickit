import asyncio
from collections import defaultdict

import pytest

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
def internal_state_consumer():
    return InternalStateConsumer(["Test"])


@pytest.fixture
def internal_state_producer():
    return InternalStateProducer()


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
    assert not internal_state_server.poll("Test", 0)


def test_internal_state_server_push_adds_message(
    internal_state_server: InternalStateServer,
):
    internal_state_server.create_topic("Test")
    internal_state_server.push("Test", Message("TestMessage"))
    assert Message("TestMessage") in internal_state_server.poll("Test", 0)


def test_internal_state_server_poll_excludes_prior(
    internal_state_server: InternalStateServer,
):
    internal_state_server.create_topic("Test")
    internal_state_server.push("Test", Message("TestMessage"))
    assert Message("TestMessage") not in internal_state_server.poll("Test", 1)


def test_internal_state_consumer_is_state_consumer():
    assert isinstance(InternalStateConsumer, StateConsumer)


def test_internal_state_consumer_consumes(
    internal_state_server: InternalStateServer,
    internal_state_consumer: InternalStateConsumer,
):
    internal_state_server.push("Test", Message("TestMessage"))
    assert "TestMessage" == asyncio.run(internal_state_consumer.consume().__anext__())


def test_internal_state_consumer_does_not_reconsume(
    internal_state_server: InternalStateServer,
    internal_state_consumer: InternalStateConsumer,
):
    internal_state_server.push("Test", Message("TestMessage"))
    asyncio.run(internal_state_consumer.consume().__anext__())
    assert asyncio.run(internal_state_consumer.consume().__anext__()) is None


def test_internal_state_consumer_consumes_multiple(
    internal_state_server: InternalStateServer,
    internal_state_consumer: InternalStateConsumer,
):
    internal_state_server.push("Test", Message("TestMessage"))
    internal_state_server.push("Test", Message("OtherTestMessage"))
    assert "TestMessage" == asyncio.run(internal_state_consumer.consume().__anext__())
    assert "OtherTestMessage" == asyncio.run(
        internal_state_consumer.consume().__anext__()
    )


def test_internal_state_producer_is_state_producer():
    assert isinstance(InternalStateProducer, StateProducer)


def test_internal_state_producer_produces(
    internal_state_server: InternalStateServer,
    internal_state_producer: InternalStateProducer,
):
    asyncio.run(internal_state_producer.produce("Test", "TestMessage"))
    assert Message("TestMessage") in internal_state_server.poll("Test", 0)
