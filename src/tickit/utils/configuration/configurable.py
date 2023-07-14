from typing import Any, Type, Union

from pydantic.v1 import Field, ValidationError, create_model, BaseConfig, Extra
from pydantic.v1.error_wrappers import ErrorWrapper
from typing_extensions import Literal


class StrictConfig(BaseConfig):
    extra = Extra.forbid


def as_tagged_union(
    super_cls: Type
) -> Type:
    super_cls._ref_classes = set()
    super_cls._model = None

    def __init_subclass__(cls) -> None:
        print(f"init_subclass: {cls}:{super_cls}")
        cls._ref_classes.add(cls)
        cls.__annotations__["type"] = Literal[cls.__name__]
        setattr(cls, "type", cls.__name__)

    def __get_validators__(cls) -> Any:
        print("get_validators")
        yield cls.__validate__

    def __validate__(cls, v: Any) -> Any:
        if cls._model is None:
            root = Union[tuple(cls._ref_classes)]
            cls._model = create_model(
                super_cls.__name__,
                __root__=(root, Field(..., discriminator="type")),
            )

        try:
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

    for method in __init_subclass__, __get_validators__, __validate__:
        setattr(super_cls, method.__name__, classmethod(method))

    return super_cls
