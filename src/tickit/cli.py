"""Backwards-compatible CLI entry point.

This module re-exports the CLI ``main`` group from ``tickit.__main__``
to preserve compatibility with code that imports from ``tickit.cli``.
"""

from tickit.__main__ import (
    app,
    build_simulation,
    components,
    interfaces,
    logging,
    main,
    scheduler,
)

__all__ = [
    "app",
    "build_simulation",
    "components",
    "interfaces",
    "logging",
    "main",
    "scheduler",
]
