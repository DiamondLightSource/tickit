import sys
import warnings

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    cached_property = property
    warnings.warn(
        "Property caching is not performed when running with python versions prior to"
        + "3.8. Performance may be degraded.",
        RuntimeWarning,
    )

__all__ = ["cached_property"]
