from typing import Any


class Singleton(type):
    """A singleton metaclass, which allows only one instance of derived types."""

    _instances: dict["Singleton", "Singleton"] = {}

    def __call__(self, *args: Any, **kwargs: Any) -> "Singleton":
        """Return the class instance, if uninstantiated create an instance."""
        if self not in self._instances:
            self._instances[self] = super().__call__(*args, **kwargs)
        return self._instances[self]
