from dataclasses import is_dataclass, make_dataclass
from inspect import Parameter, signature
from typing import Any, Callable, Dict, Iterator, Sequence, Set, Type, TypeVar

from apischema import deserializer, serializer
from apischema.conversions.conversions import Conversion
from apischema.tagged_unions import Tagged, TaggedUnion, get_tagged

from tickit.utils.compat.typing_compat import Protocol, runtime_checkable

# Implementation adapted from apischema example: Class as tagged union of its subclasses
# see: https://wyfo.github.io/apischema/examples/subclass_tagged_union/

#: A function or method
Func = TypeVar("Func", bound=Callable)
#: A class
Cls = TypeVar("Cls", bound=type)
#: A configurable type
T = TypeVar("T", covariant=True)


def rec_subclasses(cls: type) -> Iterator[type]:
    """Recursive implementation of type.__subclasses__.

    Args:
        cls (Type): The base class.

    Returns:
        Iterator[type]: An iterator of subclasses.
    """
    for sub_cls in cls.__subclasses__():
        yield sub_cls
        yield from rec_subclasses(sub_cls)


def configurable_alias(sub: Type) -> str:
    """Gets the alias of a configurable sub-class.

    Args:
        sub (Type): The sub-class to be aliased.

    Returns:
        str: The alias assigned to the sub-class.
    """
    return sub.configures().__module__ + "." + sub.configures().__name__


def configurable_base(cls: Cls) -> Cls:
    """A decorator to make a config base class which can deserialize aliased sub-classes.

    A decorator which makes a config class the root of a tagged union of sub-classes
    allowing for serialization and deserialization of config trees by class alias. The
    function registers both an apischema serialization and an apischema deserialization
    conversion for the base class which perform lookup based on a tagged union of
    aliased sub-classes.

    Args:
        cls (Cls): The config base class.

    Returns:
        Cls: The modified config base class.
    """

    def serialization() -> Conversion:
        """Create an apischema Conversion with a converter for recursive sub-classes.

        Returns:
            Conversion: An apischema Conversion with a converter for recursive
                sub-classes.
        """
        serialization_union = type(
            cls.__name__,
            (TaggedUnion,),
            {
                "__annotations__": {
                    configurable_alias(sub): Tagged[sub]  # type: ignore
                    for sub in rec_subclasses(cls)
                }
            },
        )
        return Conversion(
            lambda obj: serialization_union(**{configurable_alias(obj.__class__): obj}),
            source=cls,
            target=serialization_union,
            inherited=False,
        )

    def deserialization() -> Conversion:
        """Create an apischema Conversion which gets a sub-class by tag.

        Returns:
            Conversion: An apischema Conversion which gets a sub-class by tag.
        """
        annotations: Dict[str, Any] = {}
        deserialization_namespace: Dict[str, Any] = {"__annotations__": annotations}
        for sub in rec_subclasses(cls):
            annotations[configurable_alias(sub)] = Tagged[sub]  # type: ignore
        deserialization_union = type(
            cls.__name__,
            (TaggedUnion,),
            deserialization_namespace,
        )
        return Conversion(
            lambda obj: get_tagged(obj)[1], source=deserialization_union, target=cls
        )

    deserializer(lazy=deserialization, target=cls)
    serializer(lazy=serialization, source=cls)
    return cls


@runtime_checkable
class Config(Protocol[T]):
    """An interface for types which implement configurations."""

    @staticmethod
    def configures() -> Type[T]:
        """A static method which returns the class configured by this config.

        Returns:
            Type[T]: The class configured by this config.
        """
        pass

    @property
    def kwargs(self) -> Dict[str, object]:
        """A property which returns the key word arguments of the configured class.

        Returns:
            Dict[str, object]: The key word argument of the configured class.
        """
        pass


def configurable(template: Type, ignore: Sequence[str] = []) -> Callable[[Type], Type]:
    """A decorator to add a config data container sub-class to a class.

    A decorator to make a class configurable by adding a config data container
    sub-class which is typically registered against a configurable base class allowing
    for serialization & deserialization by union tagging.

    Args:
        template (Type): A template dataclass from which fields are borrwoed
        ignore (Sequence[str]): Fields which should not be serialized / deserialized.
            Defaults to [].

    Returns:
        Callable[[Type], Type]: A decorator which adds the config data container.
    """
    assert is_dataclass(template)

    def add_config(cls: Type) -> Type:
        """A decorator to add a config data container sub-class to a class.

        Args:
            cls (Type): The class to which the config data container should be added.

        Returns:
            Type: The modified class.
        """

        def configures() -> Type:
            return cls

        def kwargs(self) -> Dict[str, object]:
            remove: Set[str] = (
                set(template.__annotations__)
                if hasattr(template, "__annotations__")
                else set()
            )
            return {k: self.__dict__[k] for k in set(self.__dict__) - remove}

        signature_items = set(
            (name, param)
            for typ in (template, cls)
            for name, param in signature(typ).parameters.items()
            if name not in ignore
        )

        config_data_class: Type = make_dataclass(
            f"{cls.__name__}Config",
            sorted(
                (
                    (name, param.annotation)
                    if param.default is Parameter.empty
                    else (name, param.annotation, param.default)
                    for name, param in signature_items
                ),
                key=len,
            ),
            bases=(template,),
            namespace={
                "configures": staticmethod(configures),
                "kwargs": property(kwargs),
                "__doc__": cls.__init__.__doc__,
            },
        )

        setattr(cls, config_data_class.__qualname__, config_data_class)
        return cls

    return add_config
