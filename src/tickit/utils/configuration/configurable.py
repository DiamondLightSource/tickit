from dataclasses import field
from typing import Any, Callable, Literal, Optional, Type, Union

from pydantic.v1 import BaseConfig, Extra, Field, ValidationError, create_model
from pydantic.v1.error_wrappers import ErrorWrapper


class LooseConfig(BaseConfig):
    extra: Extra = Extra.allow


class StrictConfig(BaseConfig):
    extra: Extra = Extra.forbid


def as_tagged_union(
    super_cls: Optional[Union[Type, Callable[[Type], Type]]] = None,
    *,
    discriminator: str = "type",
    config: Optional[Type[BaseConfig]] = None,
) -> Union[Type, Callable[[Type], Type]]:
    """Add all subclasses of super_cls to a discriminated union.

    For all subclasses of super_cls, add a discriminator field to identify
    the type. Raw JSON should look like {"type": <type name>, params for
    <type name>...}.
    Add validation methods to super_cls so it can be parsed by pydantic.parse_obj_as.

    Example::

        @as_tagged_union
        class Expression(ABC):
            @abstractmethod
            def calculate(self) -> int:
                ...


        @dataclass
        class Add(Expression):
            left: Expression
            right: Expression

            def calculate(self) -> int:
                return self.left.calculate() + self.right.calculate()


        @dataclass
        class Subtract(Expression):
            left: Expression
            right: Expression

            def calculate(self) -> int:
                return self.left.calculate() - self.right.calculate()


        @dataclass
        class IntLiteral(Expression):
            value: int

            def calculate(self) -> int:
                return self.value


        my_sum = Add(IntLiteral(5), Subtract(IntLiteral(10), IntLiteral(2)))
        assert my_sum.calculate() == 13

        assert my_sum == parse_obj_as(
            Expression,
            {
                "type": "Add",
                "left": {"type": "IntLiteral", "value": 5},
                "right": {
                    "type": "Subtract",
                    "left": {"type": "IntLiteral", "value": 10},
                    "right": {"type": "IntLiteral", "value": 2},
                },
            },
        )

    Args:
        super_cls: The superclass of the union, Expression in the above example
        discriminator: The discriminator that will be inserted into the
            serialized documents for type determination. Defaults to "type".
        config: A pydantic config class to be inserted into all
            subclasses. Defaults to None.

    Returns:
        Union[Type, Callable[[Type], Type]]: A decorator that adds the necessary
            functionality to a class.
    """

    def wrap(cls):
        return _as_tagged_union(cls, discriminator, config)

    # Work out if the call was @discriminated_union_of_subclasses or
    # @discriminated_union_of_subclasses(...)
    if super_cls is None:
        return wrap
    else:
        return wrap(super_cls)


def qualified_class_name(klass):
    module = klass.__module__
    if module == "builtins":
        return klass.__qualname__  # avoid outputs like 'builtins.str'
    return module + "." + klass.__qualname__


def _as_tagged_union(
    super_cls: Type,
    discriminator: str,
    config: Optional[Type[BaseConfig]] = None,
) -> Union[Type, Callable[[Type], Type]]:
    super_cls._ref_classes = set()
    super_cls._model = None
    print(super_cls.__dict__)
    print(f"as_tagged_union: {super_cls}")

    def __init_subclass__(cls, **kwargs) -> None:
        print(f"__init_subclass__: {cls}:{super_cls}")
        super_cls._model = None
        cls_name = qualified_class_name(cls)
        # Keep track of inherting classes in super class
        super_cls._ref_classes.add(cls)

        # Add a discriminator field to the class so it can
        # be identified when deserailizing.
        cls.__annotations__ = {
            **cls.__annotations__,
            discriminator: Literal[cls_name],
        }
        setattr(cls, discriminator, field(default=cls_name, repr=False))

    def __get_validators__(cls) -> Any:
        yield cls.__validate__

    def __validate__(cls, v: Any) -> Any:
        # Lazily initialize model on first use because this
        # needs to be done once, after all subclasses have been
        # declared
        print("VALIDATE")
        print(cls._model)
        if cls._model is None:
            print("foo")
            print(super_cls._ref_classes)
            root = Union[tuple(super_cls._ref_classes)]  # type: ignore
            print(f"root: {root}")
            cls._model = create_model(
                super_cls.__name__,
                __root__=(root, Field(..., discriminator=discriminator)),
                __config__=config,
            )
        print(cls._model)
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

    # Inject magic methods into super_cls
    for method in __init_subclass__, __get_validators__, __validate__:
        setattr(super_cls, method.__name__, classmethod(method))  # type: ignore

    return super_cls
