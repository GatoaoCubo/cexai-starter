"""Programmatic feature registry -- the library half of dual invocation (W3).

A *feature* is any callable registered under a name. ``run_feature`` is the single
library entrypoint that the CLI also calls, so both invocation paths converge on
the exact same callable and return the exact same object (spec P3 "identical
functional output", FR-006).

The registry is a process-global dict, mirroring the llm provider registry in
``cexai.foundation.llm``; tests snapshot and restore it for isolation.
``UnknownFeatureError`` (rooted at the package's ``CexaiError``) is raised for an
unregistered name and maps to a CLI exit code in ``cli.py``.

Article VIII (anti-abstraction): the registry is a plain late-binding map, not a
class hierarchy -- a feature is just a callable.

absorbs: 08_goose/dual-invocation
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "register_feature",
    "run_feature",
    "get_feature",
    "available_features",
    "UnknownFeatureError",
]


class UnknownFeatureError(CexaiError):
    """Raised when a feature name is not registered.

    Carries ``feature_name`` and the sorted ``available`` names as structured
    attributes so callers (and the CLI) can report precisely without parsing the
    message."""

    def __init__(self, feature_name: str, available: tuple[str, ...]) -> None:
        self.feature_name = feature_name
        self.available = available
        listed = ", ".join(available) if available else "(none registered)"
        super().__init__(f"unknown feature {feature_name!r}; available: {listed}")


# Live registry of features by name. Empty until register_feature is called.
_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_feature(name: str, fn: Callable[..., Any]) -> None:
    """Register (or override) the callable served under ``name``.

    Overriding is allowed and silent: the registry is a simple late-binding map,
    and W4/W5 deliberately re-register names as real features replace stubs."""
    _REGISTRY[name] = fn


def get_feature(name: str) -> Callable[..., Any]:
    """Return the callable registered under ``name``.

    Raises ``UnknownFeatureError(name, available_features())`` if not registered."""
    fn = _REGISTRY.get(name)
    if fn is None:
        raise UnknownFeatureError(name, available_features())
    return fn


def run_feature(name: str, *args: Any, **kwargs: Any) -> Any:
    """Resolve ``name`` and invoke it with ``*args, **kwargs``, returning its
    result unchanged.

    THE library entrypoint. The CLI dispatches through this same function so both
    interfaces share one code path -- the structural guarantee behind CLI/library
    parity (spec P3, SC-003)."""
    return get_feature(name)(*args, **kwargs)


def available_features() -> tuple[str, ...]:
    """All registered feature names, sorted for stable enumeration."""
    return tuple(sorted(_REGISTRY))
