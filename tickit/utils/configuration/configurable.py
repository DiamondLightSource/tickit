from typing import Any, DefaultDict, Dict, Iterator, Type, TypeVar

from apischema import deserializer
from apischema.conversions import Conversion
from apischema.tagged_unions import Tagged, TaggedUnion, get_tagged

# Implementation adapted from apischema example: Class as tagged union of its subclasses
# see: https://wyfo.github.io/apischema/examples/subclass_tagged_union/

#: A class
Cls = TypeVar("Cls", bound=type)


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


#: Whether the current class is registered as a tagged union
is_tagged_union: Dict[Type[Any], bool] = DefaultDict(lambda: False)


def as_tagged_union(cls: Cls) -> Cls:
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
    # This will only be used if we want to generate a json schema (which we will)
    def deserialization() -> Conversion:
        annotations: Dict[str, Any] = {}
        deserialization_namespace: Dict[str, Any] = {"__annotations__": annotations}
        for sub in rec_subclasses(cls):
            fullname = sub.__module__ + "." + sub.__name__
            annotations[fullname] = Tagged[sub]  # type: ignore
        deserialization_union = type(
            cls.__name__ + "TaggedUnion",
            (TaggedUnion,),
            deserialization_namespace,
        )
        return Conversion(
            lambda obj: get_tagged(obj)[1], source=deserialization_union, target=cls
        )

    deserializer(lazy=deserialization, target=cls)
    is_tagged_union[cls] = True
    return cls
