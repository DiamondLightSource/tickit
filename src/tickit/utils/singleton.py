from typing import Any


class Singleton(type):
    """A singleton metaclass, which allows only one instance of derived types."""

    _instances: dict["Singleton", "Singleton"] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> "Singleton":
        """Return the class instance, if uninstantiated create an instance."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
