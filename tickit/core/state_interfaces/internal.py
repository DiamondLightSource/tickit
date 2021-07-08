from typing import Collection


class InternalStateConsumer:
    def __init__(self) -> None:
        raise NotImplementedError

    async def consume(self) -> object:
        raise NotImplementedError


class InternalStateProducer:
    def __init__(self) -> None:
        raise NotImplementedError

    async def produce(self, value: object) -> None:
        raise NotImplementedError


class InternalStateTopicManager:
    def __init__(self) -> None:
        raise NotImplementedError

    async def get_topics(self) -> Collection[str]:
        raise NotImplementedError

    async def create_topic(self, topic: str) -> None:
        raise NotImplementedError

    async def remove_topic(self, topic: str) -> None:
        raise NotImplementedError
