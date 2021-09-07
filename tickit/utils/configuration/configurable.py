from dataclasses import is_dataclass, make_dataclass
from inspect import Parameter, signature
from typing import Any, Callable, Dict, Iterator, Sequence, Set, Type, TypeVar

from apischema import deserializer, serializer
from apischema.conversions.conversions import Conversion
from apischema.tagged_unions import Tagged, TaggedUnion, get_tagged

from tickit.utils.compat.typing_compat import Protocol, runtime_checkable

# Implementation adapted from apischema example: Class as tagged union of its subclasses
# see: https://wyfo.github.io/apischema/examples/subclass_tagged_union/

Func = TypeVar("Func", bound=Callable)
Cls = TypeVar("Cls", bound=type)
T = TypeVar("T", covariant=True)


def rec_subclasses(cls: type) -> Iterator[type]:
    """Recursive implementation of type.__subclasses__"""
    for sub_cls in cls.__subclasses__():
        yield sub_cls
        yield from rec_subclasses(sub_cls)


def configurable_alias(sub: Type) -> str:
    return sub.configures().__module__ + "." + sub.configures().__name__


def configurable_base(cls: Cls) -> Cls:
    def serialization() -> Conversion:
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
        annotations: Dict[str, Any] = {}
        deserialization_namespace: Dict[str, Any] = {"__annotations__": annotations}
        for sub in rec_subclasses(cls):
            annotations[configurable_alias(sub)] = Tagged[sub]  # type: ignore
        deserialization_union = type(
            cls.__name__, (TaggedUnion,), deserialization_namespace,
        )
        return Conversion(
            lambda obj: get_tagged(obj)[1], source=deserialization_union, target=cls
        )

    deserializer(lazy=deserialization, target=cls)
    serializer(lazy=serialization, source=cls)
    return cls


@runtime_checkable
class Config(Protocol[T]):
    @staticmethod
    def configures() -> Type[T]:
        pass

    @property
    def kwargs(self) -> Dict[str, object]:
        pass


def configurable(template: Type, ignore: Sequence[str] = []) -> Callable[[Type], Type]:
    assert is_dataclass(template)

    def add_config(cls: Type) -> Type:
        def configures() -> Type:
            return cls

        def kwargs(self) -> Dict[str, object]:
            remove: Set[str] = set(template.__annotations__) if hasattr(
                template, "__annotations__"
            ) else set()
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
            },
        )

        setattr(cls, "Config", config_data_class)
        return cls

    return add_config
