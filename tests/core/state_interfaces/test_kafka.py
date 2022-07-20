from typing import Iterable

import pytest
import pytest_asyncio
from mock import AsyncMock, Mock, patch

from tickit.core.state_interfaces.kafka import KafkaStateConsumer, KafkaStateProducer


@pytest.fixture
def mock_callback() -> AsyncMock:
    async def callback_fn(input: str) -> None:
        return None

    return AsyncMock(spec_set=callback_fn)


@pytest.fixture
def patch_AIOKafkaStateProducer() -> Iterable[Mock]:
    with patch(
        "tickit.core.state_interfaces.kafka.AIOKafkaProducer", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
def patch_AIOKafkaStateConsumer() -> Iterable[Mock]:
    with patch(
        "tickit.core.state_interfaces.kafka.AIOKafkaConsumer", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
def patch_kafka_state_consumer_run_forever_method() -> Iterable[Mock]:
    with patch.object(KafkaStateConsumer, "_run_forever") as mock:
        yield mock


@pytest_asyncio.fixture
async def kafka_state_consumer(
    mock_callback: AsyncMock,
    patch_AIOKafkaStateConsumer: Mock,
    patch_kafka_state_consumer_run_forever_method: Mock,
):
    return KafkaStateConsumer(callback=mock_callback)


@pytest.fixture
def kafka_state_producer(
    mock_callback: AsyncMock,
    patch_AIOKafkaStateProducer: Mock,
):
    return KafkaStateProducer()


@pytest.mark.asyncio
async def test_kafka_state_consumer_constructor(
    kafka_state_consumer: KafkaStateConsumer,
):
    kafka_state_consumer._run_forever.assert_called_once()  # type: ignore
    pass


@pytest.mark.asyncio
async def test_kafka_state_consumer_subscribe(
    kafka_state_consumer: KafkaStateConsumer,
):
    await kafka_state_consumer.subscribe(["foo", "bar"])
    kafka_state_consumer.consumer.subscribe.assert_called_once_with(["foo", "bar"])


@pytest.mark.asyncio
async def test_kafka_state_producer_constructor(
    patch_AIOKafkaStateProducer: Mock,
):
    _: KafkaStateProducer = KafkaStateProducer()


@pytest.mark.asyncio
async def test_kafka_state_producer_produce(
    patch_AIOKafkaStateProducer: Mock,
):
    producer: KafkaStateProducer = KafkaStateProducer()
    await producer.produce("foo", 42)
    producer.producer.send.assert_awaited_once_with("foo", 42)
