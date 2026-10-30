from collections.abc import Callable
from dataclasses import field
from functools import reduce
from importlib import import_module
from typing import Any, Literal, TypeVar, overload

from pydantic import ConfigDict, Field, TypeAdapter, ValidationError, create_model

_T = TypeVar("_T", bound=type)


# When called with a class: return the same class (enables Pylance to see _validate)
@overload
def as_tagged_union(
    super_cls: _T, *, discriminator: str = ..., config: type[ConfigDict] | None = ...
) -> _T: ...


# When called without args: return a decorator that wraps a class
@overload
def as_tagged_union(
    super_cls: None = None,
    *,
    discriminator: str = ...,
    config: type[ConfigDict] | None = ...,
) -> Callable[[_T], _T]: ...


def as_tagged_union(
    super_cls: _T | None = None,
    *,
    discriminator: str = "type",
    config: type[ConfigDict] | None = None,
) -> _T | Callable[[_T], _T]:
    def wrap(cls):
        return _as_tagged_union(cls, discriminator, config)

    # Work out if the call was @as_tagged_union or
    # @as_tagged_union(...)
    if super_cls is None:
        return wrap  # pyright: ignore[reportReturnType]
    else:
        return wrap(super_cls)  # type: ignore[return-value]


def _as_tagged_union(
    super_cls: type,
    discriminator: str,
    config: type[ConfigDict] | None = None,
) -> type | Callable[[type], type]:
    super_cls._ref_classes = set()
    super_cls._model = None
    setattr(super_cls, discriminator, field())

    def _load_module_with_type(values: dict[str, str]) -> None:
        fullname = values.get(discriminator)
        if fullname:
            pkg, clsname = fullname.rsplit(".", maxsplit=1)
            getattr(import_module(pkg), clsname)

    def __init_subclass__(cls) -> None:
        super_cls._model = None
        cls_name = f"{cls.__module__}.{cls.__qualname__}"
        # Keep track of inheriting classes in super class
        super_cls._ref_classes.add(cls)

        # Add a discriminator field to the class so it can
        # be identified when deserializing.
        cls.__annotations__ = {
            **getattr(cls, "__annotations__", {}),
            # Literal is supposed to only accept literal strings but we need to
            # set it dynamically
            discriminator: Literal[cls_name],  # type: ignore
        }
        setattr(cls, discriminator, field(default=cls_name, repr=False))

    def _validate(cls, v: Any) -> Any:
        _load_module_with_type(v)

        if cls._model is None:
            discriminator_value = v.get(discriminator) if isinstance(v, dict) else None
            if discriminator_value:
                for ref_cls in super_cls._ref_classes:
                    cls_name = f"{ref_cls.__module__}.{ref_cls.__qualname__}"
                    if cls_name == discriminator_value:
                        return TypeAdapter(ref_cls).validate_python(v)

            if len(super_cls._ref_classes) == 1:
                single_subclass = next(iter(super_cls._ref_classes))
                return TypeAdapter(single_subclass).validate_python(v)
            root = reduce(lambda a, b: a | b, super_cls._ref_classes)
            super_cls._model = create_model(
                super_cls.__name__,
                __root__=(root, Field(...)),
            )
        try:
            if cls._model:
                return TypeAdapter(cls._model).validate_python(v)
        except ValidationError as e:
            for err in e.errors():
                if err.get("loc") and err["loc"][0] == "__root__":
                    err["loc"] = err["loc"][1:]
            raise e

    # Inject magic methods into super_cls
    for method in __init_subclass__, _validate:
        setattr(super_cls, method.__name__, classmethod(method))  # type: ignore

    return super_cls
