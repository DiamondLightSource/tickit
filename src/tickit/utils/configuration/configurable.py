from dataclasses import field
from importlib import import_module
from typing import Any, Callable, Literal, Optional, Type, Union

try:
    from pydantic.v1 import (
        BaseConfig,
        Field,
        ValidationError,
        create_model,
        parse_obj_as,
    )
    from pydantic.v1.error_wrappers import ErrorWrapper
except ImportError:
    from pydantic import (  # type: ignore
        BaseConfig,
        Field,
        ValidationError,
        create_model,
        parse_obj_as,
    )
    from pydantic.error_wrappers import ErrorWrapper  # type: ignore


def as_tagged_union(
    super_cls: Optional[Union[Type, Callable[[Type], Type]]] = None,
    *,
    discriminator: str = "type",
    config: Optional[Type[BaseConfig]] = None,
) -> Union[Type, Callable[[Type], Type]]:
    def wrap(cls):
        return _as_tagged_union(cls, discriminator, config)

    # Work out if the call was @discriminated_union_of_subclasses or
    # @discriminated_union_of_subclasses(...)
    if super_cls is None:
        return wrap
    else:
        return wrap(super_cls)


def _as_tagged_union(
    super_cls: Type,
    discriminator: str,
    config: Optional[Type[BaseConfig]] = None,
) -> Union[Type, Callable[[Type], Type]]:
    super_cls._ref_classes = set()
    super_cls._model = None
    setattr(super_cls, discriminator, field())

    def _load_module_with_type(values: dict[str, str]) -> None:
        fullname = values.get(discriminator)
        assert fullname
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
            discriminator: Literal[cls_name],
        }
        setattr(cls, discriminator, field(default=cls_name, repr=False))

    def __get_validators__(cls) -> Any:
        yield cls.__validate__

    def __validate__(cls, v: Any) -> Any:
        _load_module_with_type(v)

        if cls._model is None:
            if len(super_cls._ref_classes) == 1:
                single_subclass = next(iter(super_cls._ref_classes))
                return parse_obj_as(single_subclass, v)
            root = Union[tuple(super_cls._ref_classes)]  # type: ignore
            super_cls._model = create_model(
                super_cls.__name__,
                __root__=(root, Field(..., discriminator=discriminator)),
                __config__=config,
            )
        try:
            assert cls._model
            return cls._model(__root__=v).__root__
        except ValidationError as e:
            for (
                error
            ) in e.raw_errors:  # need in to remove redundant __root__ from error path
                if (
                    isinstance(error, ErrorWrapper)
                    and error.loc_tuple()[0] == "__root__"
                ):
                    error._loc = error.loc_tuple()[1:]

            raise e

    # Inject magic methods into super_cls
    for method in __init_subclass__, __get_validators__, __validate__:
        setattr(super_cls, method.__name__, classmethod(method))  # type: ignore

    return super_cls
