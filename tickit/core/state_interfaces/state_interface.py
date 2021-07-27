import sys
from typing import (
    AsyncIterator,
    Callable,
    Dict,
    Iterable,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
)

# TODO: Investigate why import from tickit.utils.compat.typing_compat causes mypy error
# See mypy issue for details: https://github.com/python/mypy/issues/10851
if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable

C = TypeVar("C", covariant=True)
P = TypeVar("P", contravariant=True)


@runtime_checkable
class StateConsumer(Protocol[C]):
    def __init__(self, consume_topics: Iterable[str]) -> None:
        ...

    async def consume(self) -> AsyncIterator[Optional[C]]:
        if False:
            yield


@runtime_checkable
class StateProducer(Protocol[P]):
    def __init__(self) -> None:
        ...

    async def produce(self, topic: str, value: P) -> None:
        ...


StateInterface = TypeVar("StateInterface", StateConsumer, StateProducer)


consumers: Dict[str, Tuple[Type[StateConsumer], bool]] = dict()
producers: Dict[str, Tuple[Type[StateProducer], bool]] = dict()


def add(
    name: str, external: bool
) -> Callable[[Type[StateInterface]], Type[StateInterface]]:
    def wrap(interface: Type[StateInterface]) -> Type[StateInterface]:
        if isinstance(interface, StateConsumer):
            consumers[name] = (interface, external)
        elif isinstance(interface, StateProducer):
            producers[name] = (interface, external)
        else:
            Warning(
                "{} is not {} or {}".format(interface, StateConsumer, StateProducer)
            )
        return interface

    return wrap


def interfaces(external: bool = False) -> Set[str]:
    return satisfy_externality(external, consumers) & satisfy_externality(
        external, producers
    )


def satisfy_externality(
    external: bool, interfaces: Dict[str, Tuple[Type[StateInterface], bool]]
) -> Set[str]:
    return set(
        name for name, interface in interfaces.items() if not external or interface[1]
    )


def get(name: str) -> Tuple[Type[StateConsumer], Type[StateProducer]]:
    return consumers[name][0], producers[name][0]
