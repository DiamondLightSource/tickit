from collections import defaultdict
from dataclasses import is_dataclass, make_dataclass
from inspect import signature
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Sequence,
    Set,
    Type,
    TypeVar,
    get_type_hints,
)

from apischema import deserializer, serializer
from apischema.conversions.conversions import Conversion
from apischema.metadata import conversion
from apischema.objects.conversions import object_deserialization
from apischema.tagged_unions import Tagged, TaggedUnion, get_tagged
from apischema.type_names import type_name
from apischema.utils import to_pascal_case
from yaml import Dumper, Node

# Implementation adapted from apischema example: Class as tagged union of its subclasses
# see: https://wyfo.github.io/apischema/examples/subclass_tagged_union/

_alternative_constructors: Dict[Type, List[Callable]] = defaultdict(list)
Func = TypeVar("Func", bound=Callable)


def alternative_constructor(func: Func) -> Func:
    _alternative_constructors[get_type_hints(func)["return"]].append(func)
    return func


def rec_subclasses(cls: type) -> Iterator[type]:
    """Recursive implementation of type.__subclasses__"""
    for sub_cls in cls.__subclasses__():
        yield sub_cls
        yield from rec_subclasses(sub_cls)


Cls = TypeVar("Cls", bound=type)


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
            for constructor in _alternative_constructors.get(sub, ()):
                alias = to_pascal_case(constructor.__name__)
                constructor.__annotations__["return"] = sub
                annotations[alias] = Tagged[sub]  # type: ignore
                deserialization_namespace[alias] = Tagged(
                    conversion(
                        deserialization=object_deserialization(
                            constructor, type_name(alias)
                        )
                    )
                )
        deserialization_union = type(
            cls.__name__, (TaggedUnion,), deserialization_namespace,
        )
        return Conversion(
            lambda obj: get_tagged(obj)[1], source=deserialization_union, target=cls
        )

    deserializer(lazy=deserialization, target=cls)
    serializer(lazy=serialization, source=cls)
    return cls


def represent_aliased_str(dumper: Dumper, data: str) -> Node:
    return dumper.represent_str(data)


def configurable(template: Type, ignore: Sequence[str] = []) -> Callable[[Type], Type]:
    assert is_dataclass(template)

    def add_config(cls: Type) -> Type:
        def configures() -> Type:
            return cls

        def __kwargs__(self) -> Dict[str, object]:
            remove: Set[str] = set(template.__annotations__) if hasattr(
                template, "__annotations__"
            ) else set()
            return {k: self.__dict__[k] for k in set(self.__dict__) - remove}

        config_data_class: Type = make_dataclass(
            f"{cls.__name__}Config",
            set(
                (name, param.annotation)
                for c in (template, cls)
                for name, param in signature(c).parameters.items()
                if name not in ignore
            ),
            bases=(template,),
            namespace={
                "configures": staticmethod(configures),
                "__kwargs__": property(__kwargs__),
            },
        )

        setattr(cls, "Config", config_data_class)
        return cls

    return add_config
