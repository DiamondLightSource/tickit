from typing import Collection, Protocol, runtime_checkable


@runtime_checkable
class StateConsumer(Protocol):
    def __init__(self, consume_topics: Collection[str]) -> None:
        ...

    async def consume(self) -> object:
        ...


@runtime_checkable
class StateProducer(Protocol):
    def __init__(self, produce_topic: str) -> None:
        ...

    async def produce(self, topic: str, value: object) -> None:
        ...


@runtime_checkable
class StateTopicManager(Protocol):
    def __init__(self) -> None:
        ...

    async def get_topics(self) -> Collection[str]:
        ...

    async def create_topic(self, topic: str) -> None:
        ...

    async def remove_topic(self, topic: str):
        ...
