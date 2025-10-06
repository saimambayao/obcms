"""Compatibility wrapper for the historic `policy_tracking` module.

The policy tracking app was relocated under `recommendations.policy_tracking`
but large portions of the codebase – including shared tests – still import
`policy_tracking.*`.  This wrapper keeps those imports working by proxying to
the canonical package while emitting a gentle reminder to update imports when
the opportunity arises.
"""

from __future__ import annotations

import sys
import warnings
from importlib import import_module
from types import ModuleType


_DEPRECATION_MSG = (
    "policy_tracking.* modules now live under recommendations.policy_tracking.*. "
    "Please update imports to the new path."
)


def _proxy_module(module_name: str) -> ModuleType:
    """Import a submodule from the canonical package and register it here."""

    full_name = f"recommendations.policy_tracking.{module_name}"
    module = import_module(full_name)
    sys.modules[f"{__name__}.{module_name}"] = module
    return module


# Surface the canonical package attributes at the package level.
_canonical_pkg = import_module("recommendations.policy_tracking")

for attr, value in vars(_canonical_pkg).items():
    if not attr.startswith("__"):
        globals().setdefault(attr, value)


# Pre-register the common submodules expected by legacy imports.
for _name in [
    "apps",
    "models",
    "serializers",
    "views",
    "admin",
    "api_views",
    "api_urls",
    "migrations",
    "management",
]:
    try:
        _proxy_module(_name)
    except ModuleNotFoundError:
        # Some optional modules (like specialized APIs) may not exist. Ignore.
        continue


def __getattr__(name: str):
    """Lazily proxy remaining attributes/submodules on demand."""

    # Django test discovery looks for load_tests - don't try to proxy it
    if name == "load_tests":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)

    try:
        return globals()[name]
    except KeyError:
        module = _proxy_module(name)
        return module


__all__ = [key for key in globals().keys() if not key.startswith("_")]
