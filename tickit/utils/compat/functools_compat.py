import sys
import warnings

if sys.version_info >= (3, 8):
    from functools import cached_property  # pragma: no cover
else:
    cached_property = property  # pragma: no cover
    warnings.warn(
        "Property caching is not performed when running with python versions prior to"
        + "3.8. Performance may be degraded.",
        RuntimeWarning,
    )  # pragma: no cover

__all__ = ["cached_property"]
