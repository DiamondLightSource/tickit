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

#: A consumable value
C = TypeVar("C")
#: A producable value
P = TypeVar("P")


class Message(NamedTuple):
    """An immutable data container for internal messages."""

    value: Any


#: A list of messages
Messages = NewType("Messages", List[Message])


class InternalStateServer(metaclass=Singleton):
    """A singleton, in memory, publish/subscribe message store and router.

    A singleton, in memory, publish/subscribe message store and router. The single
    instance of this class holds a mapping of topics and a list of messages which have
    been pushed to them and a mapping of consumers which subscribe to the topics. Upon
    subscribing to a topic, a consumer is sent all of the messages which were
    previously registered against the topic. Upon pushing to a topic, the message is
    added to the store and immediately forwarded to each of the consumers which
    subscribe to the topic.
    """

    _topics: DefaultDict[str, Messages] = defaultdict(lambda: Messages(list()))
    _subscribers: DefaultDict[str, Set["InternalStateConsumer"]] = defaultdict(set)

    async def push(self, topic: str, message: Message) -> None:
        """An asynchronous method which propagates a message to subscribers and stores it.

        An asynchronous method which propagates the given message to consumers which
        subscribe to the topic and stores the message in the topic -> messages mapping.

        Args:
            topic (str): The topic on which the the message should be propagated and
                stored.
            message (Message): The message which should be propagated and stored on the
                topic.
        """
        self._topics[topic].append(message)
        for subscriber in self._subscribers[topic]:
            await subscriber.add_message(message)

    async def subscribe(self, consumer: "InternalStateConsumer", topics: Iterable[str]):
        """Subscribes the consumer to the given topics, so it is notified a message is added.

        An asynchronous method which adds a consumer to the subscriber list of each
        topic in the topics iterable. On subscription, previous messages on the topic
        are immediately passed to the consumer.

        Args:
            consumer (InternalStateConsumer): The consumer which is subscribing to the
                topic.
            topics (Iterable[str]): The topic which the consumer is to be subscribed to.
        """
        for topic in topics:
            self._subscribers[topic].add(consumer)
            for message in self._topics[topic]:
                await consumer.add_message(message)

    def create_topic(self, topic: str) -> None:
        """Creates a new topic as an empty message list.

        Args:
            topic (str): The topic to be created.
        """
        assert topic not in self._topics.keys()
        self._topics[topic] = Messages(list())

    def remove_topic(self, topic: str) -> None:
        """Removes an existing topic and the corresponding message list.

        Args:
            topic (str): The topic to be removed.
        """
        assert topic in self._topics.keys()
        del self._topics[topic]

    @property
    def topics(self) -> List[str]:
        """A list of topics which currently exist.

        Returns:
            List[str]: A list of topics which currently exist.
        """
        return list(self._topics.keys())


@state_interface.add("internal", False)
class InternalStateConsumer(Generic[C]):
    """An internal, singleton based, implementation of the StateConsumer protocol.

    A internal, singleton based, implementation of the StateConsumer protocol, this
    consumer can subscribe to InternalStateServer topics, upon recieving a message the
    consumer passes the value to the callback function passed during initialization, if
    a topic is subscribed to which does not yet exist it is created.
    """

    def __init__(self, callback: Callable[[C], Awaitable[None]]) -> None:
        """Gets an instance of the InternalStateServer for use in subscribe.

        Args:
            callback (Callable[[C], Awaitable[None]]): An asynchronous handler function
                for consumed values.
        """
        self.server = InternalStateServer()
        self.callback = callback

    async def subscribe(self, topics: Iterable[str]) -> None:
        """Subscribes the consumer to the given topics, new messages are passed to the callback.

        Args:
            topics (Iterable[str]): An iterable of topics to subscribe to.
        """
        await self.server.subscribe(self, topics)

    async def add_message(self, message: Message) -> None:
        """Adds a message to the consumer, triggering a callback.

        Args:
            message (Message): The message to be added to the consumer.
        """
        await self.callback(message.value)


@state_interface.add("internal", False)
class InternalStateProducer(Generic[P]):
    """An internal, singleton based, implementation of the StateProducer protocol.

    An internal, singleton based, implementation of the StateProducer protocol, this
    producer can produce a value to a InternalStateServer topic, if the topic does not
    yet exist it is created.
    """

    def __init__(self) -> None:
        """Gets an instance of the InternalStateServer for use in produce."""
        self.server = InternalStateServer()

    async def produce(self, topic: str, value: P) -> None:
        """Produces a value to the provided topic.

        Args:
            topic (str): The topic to which the value should be sent.
            value (P): The value to send to the provided topic.
        """
        await self.server.push(topic, Message(value=value))
