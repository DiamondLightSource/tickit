import sys
from typing import Awaitable, Callable, Dict, Iterable, Set, Tuple, Type, TypeVar
from warnings import warn

# TODO: Investigate why import from tickit.utils.compat.typing_compat causes mypy error
# See mypy issue for details: https://github.com/python/mypy/issues/10851
if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
elif sys.version_info >= (3, 5):
    from typing_extensions import Protocol, runtime_checkable

#: A consumable value
C = TypeVar("C", covariant=True)
#: A producable value
P = TypeVar("P", contravariant=True)


@runtime_checkable
class StateConsumer(Protocol[C]):
    """An interface for types which implent publish/subscribe message consumers.

    An interface for types which implement publish/subscribe message consumers,
    the consumer must be able to subscribe to topics within the messaging framework,
    upon recieving a message the consumer should pass the value to the callback
    function, if a topic is subscribed to which does not yet exist it should be created.
    """

    def __init__(self, callback: Callable[[C], Awaitable[None]]) -> None:
        """A constructor of the consumer, given a callback handle.

        Args:
            callback (Callable[[C], Awaitable[None]]): An asynchronous handler function
                for consumed values.
        """
        pass

    async def subscribe(self, topics: Iterable[str]) -> None:
        """Subscribes the consumer to the given topics, new messages are passed to the callback.

        Args:
            topics (Iterable[str]): An iterable of topics to subscribe to.
        """
        pass


@runtime_checkable
class StateProducer(Protocol[P]):
    """An interface for types which implement publish/subscribe message producers.

    An interface for types which implment publish/subscribe message producers,
    the producer must be able to produce a value to a topic within the messaging
    framework, if the topic does not yet exist it should be created.
    """

    def __init__(self) -> None:
        """A constructor of the producer, given no arguments."""
        pass

    async def produce(self, topic: str, value: P) -> None:
        """Produces a value to the provided topic.

        Args:
            topic (str): The topic to which the value should be sent.
            value (P): The value to send to the provided topic.
        """
        pass


#: The union of StateConsumer and StateProducer
StateInterface = TypeVar("StateInterface", StateConsumer, StateProducer)


consumers: Dict[str, Tuple[Type[StateConsumer], bool]] = dict()
producers: Dict[str, Tuple[Type[StateProducer], bool]] = dict()


def add(
    name: str, external: bool
) -> Callable[[Type[StateInterface]], Type[StateInterface]]:
    """A decorator to add a StateInterface to the registry.

    A decorator to add a StateInterface to the registry of StateConsumers or
    StateProducer according to it's signature. StateConsumers and StateProducers which
    are intended to work together should be added with the same name.

    Args:
        name (str): The name under which the class should be registered (typically the
            name of the messaging framework).
        external (bool): A flag which indicates whether the interface can be used
            simulations which are distributed across processes.
    """

    def wrap(interface: Type[StateInterface]) -> Type[StateInterface]:
        if isinstance(interface, StateProducer):
            producers[name] = (interface, external)
        elif isinstance(interface, StateConsumer):
            consumers[name] = (interface, external)
        else:
            warn(
                RuntimeWarning(
                    "{} is not {} or {}".format(interface, StateConsumer, StateProducer)
                )
            )
        return interface

    return wrap


def interfaces(external: bool = False) -> Set[str]:
    """Gets a set of interface names for which both a StateConsumer and StateProducer exist.

    Gets a set of interface names for which both a StateConsumer and StateProducer
    exist. The external option may be used to restrict interfaces to those which may be
    used in simulations which are distriubted across multiple processes.

    Args:
        external (bool): If true, only interfaces which can be used in simulations
            which are distributed across processes are returned. If false, all
            interfaces are returned. Defaults to False.

    Returns:
        Set[str]: A set of names of StateConsumer / StateProducer pairs.
    """
    return satisfy_externality(external, consumers) & satisfy_externality(
        external, producers
    )


def satisfy_externality(
    external: bool, interfaces: Dict[str, Tuple[Type[StateInterface], bool]]
) -> Set[str]:
    """Finds which interfaces satisfy the externality requirement provided.

    Args:
        external (bool): If true, only interfaces which can be used in
            simulations which are distributed across processes are returned. If false,
            all interfaces are returned.
        interfaces (Dict[str, Tuple[Type[StateInterface], bool]]): A mapping of
            interface names to a tuple of their class and their externality flag.

    Returns:
        Set[str]: A set of interface names which satisfy the externality requirement.
    """
    return set(
        name for name, interface in interfaces.items() if not external or interface[1]
    )


def get_interface(name: str) -> Tuple[Type[StateConsumer], Type[StateProducer]]:
    """Get the StateConsumer and StateProducer classes for a given interface name.

    Args:
        name (str): The name of the interface to be retrieved.

    Returns:
        Tuple[Type[StateConsumer], Type[StateProducer]]:
            A tuple of the StateConsumer and StateProducer classes.
    """
    return consumers[name][0], producers[name][0]
