from importlib.metadata import version

__version__ = version("tickit")
del version

__all__ = ["__version__"]
