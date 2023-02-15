import sys
import warnings

if sys.version_info >= (3, 8):
    from functools import cached_property
elif sys.version_info >= (3, 5):
    cached_property = property
    warnings.warn(
        "Property caching is not performed when running with python versions prior to"
        + "3.8. Performance may be degraded.",
        RuntimeWarning,
    )

__all__ = ["cached_property"]
