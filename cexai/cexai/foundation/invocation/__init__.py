"""Dual invocation framework: CLI + library API (W3).

Implements spec User Story P3 (Article II): every feature is invocable via
``cexai <feature>`` (text default, ``--json`` for structured output) AND via the
Python library API, with semantically equivalent results. Both paths converge on
``run_feature``, so "identical functional output" is a structural guarantee, not a
coincidence (SC-003). The ``cexai`` console script declared in pyproject.toml
resolves to ``cli:app`` here.

Public surface:
    app                 -- typer CLI (``cexai <feature> [args] [--json]``)
    register_feature    -- register a callable under a name
    run_feature         -- invoke a registered feature (the shared entrypoint)
    get_feature         -- resolve a feature callable by name
    available_features  -- list registered feature names
    to_json / to_text   -- deterministic JSON / human-readable renderers
    UnknownFeatureError  -- raised for an unregistered feature name

``invocation_interface`` EXTENDS the canonical CEX ``interface`` kind by attribute
(``interface_variant: cli | library``); it is NOT a new kind. Kind registration is
W4, not here.

absorbs: 08_goose/dual-invocation
"""

from __future__ import annotations

from cexai.foundation.invocation.cli import app
from cexai.foundation.invocation.json_io import to_json, to_text
from cexai.foundation.invocation.library import (
    UnknownFeatureError,
    available_features,
    get_feature,
    register_feature,
    run_feature,
)

__all__ = [
    "app",
    "register_feature",
    "run_feature",
    "get_feature",
    "available_features",
    "to_json",
    "to_text",
    "UnknownFeatureError",
]
