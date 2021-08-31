from collections import defaultdict
from typing import (
    Any,
    Awaitable,
    Callable,
    DefaultDict,
    Generic,
    Iterable,
    List,
    NamedTuple,
    NewType,
    Set,
    TypeVar,
)

from tickit.core.state_interfaces import state_interface
from tickit.utils.singleton import Singleton

C = TypeVar("C")
P = TypeVar("P")


class Message(NamedTuple):
    value: Any


Messages = NewType("Messages", List[Message])


class InternalStateServer(metaclass=Singleton):
    _topics: DefaultDict[str, Messages] = defaultdict(lambda: Messages(list()))
    _subscribers: DefaultDict[str, Set["InternalStateConsumer"]] = defaultdict(set)

    async def push(self, topic: str, message: Message) -> None:
        self._topics[topic].append(message)
        for subscriber in self._subscribers[topic]:
            await subscriber.add_message(message)

    async def subscribe(self, consumer: "InternalStateConsumer", topics: Iterable[str]):
        for topic in topics:
            self._subscribers[topic].add(consumer)
            for message in self._topics[topic]:
                await consumer.add_message(message)

    def create_topic(self, topic: str) -> None:
        assert topic not in self._topics.keys()
        self._topics[topic] = Messages(list())

    def remove_topic(self, topic: str) -> None:
        assert topic in self._topics.keys()
        del self._topics[topic]

    @property
    def topics(self) -> List[str]:
        return list(self._topics.keys())


@state_interface.add("internal", False)
class InternalStateConsumer(Generic[C]):
    def __init__(self, callback: Callable[[C], Awaitable[None]]) -> None:
        self.server = InternalStateServer()
        self.callback = callback

    async def subscribe(self, topics: Iterable[str]) -> None:
        await self.server.subscribe(self, topics)

    async def add_message(self, message: Message) -> None:
        await self.callback(message.value)


@state_interface.add("internal", False)
class InternalStateProducer(Generic[P]):
    def __init__(self) -> None:
        self.server = InternalStateServer()

    async def produce(self, topic: str, value: P) -> None:
        await self.server.push(topic, Message(value=value))
