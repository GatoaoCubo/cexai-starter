"""The v1 type-token registry -- the loadable single source of truth for which
type tokens exist and which validator each one uses (ADR 022 D-022-02).

A runtime loads the packaged ``type_registry.yaml`` at startup; the 12 v1 tokens
mirror the W2 ``schema.TYPE_TOKENS`` keys exactly (the list family is keyed
``list[T]``). ``register_token`` is the MINOR-version extension path (D-022-04):
it adds a custom token to the live process registry without editing this module.
``get_token`` raises ``UnknownTypeTokenError`` on a miss; ``resolve_validator``
imports a token's declared callable (D-022-02 "runtime loads validators at
startup; refuse if any fails to load").

The process registry is a lazily-loaded module global so ``register_token`` and
``get_token`` share one view; tests reset it via ``reset_registry`` (the conftest
autouse seam) so a registration never leaks or inflates the 12-token count.

YAML is parsed with PyYAML (a transitive repo dependency). If it is ever
unavailable the import error surfaces with a clear message rather than silently
degrading -- the registry is governance-critical (D-022-02 HARD FAIL at F7).

Spec provenance: cexai-specs/_decisions/adr_022_open_variables_full_protocol.md
(D-022-02 registry schema + validator contract, D-022-04 versioning).

absorbs: cexai-specs/open-variables-protocol
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cexai.foundation.open_vars.errors import OpenVarError, UnknownTypeTokenError

_logger = logging.getLogger("cexai.foundation.open_vars.registry")

try:  # PyYAML is a transitive repo dep; the registry is too critical to guess.
    import yaml as _yaml
except ImportError as _exc:  # pragma: no cover - yaml is present in the repo env
    _yaml = None
    _YAML_IMPORT_ERROR = _exc

__all__ = [
    "TokenDef",
    "load_registry",
    "register_token",
    "get_token",
    "resolve_validator",
    "reset_registry",
]

# The packaged default registry lives beside this module so it ships inside the
# package and resolves under an editable install and a source checkout alike.
_PACKAGED_REGISTRY_PATH = Path(__file__).resolve().parent / "type_registry.yaml"

# The 7 mandatory fields per D-022-02 entry schema. json_schema_ref and
# deprecated_in are optional; everything else MUST be present and truthy.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "name",
    "base_python",
    "json_form",
    "validator",
    "min_protocol_version",
    "introduced_by",
    "rationale",
)

_VALID_JSON_FORMS = frozenset(
    {"string", "integer", "number", "boolean", "array", "object"}
)


@dataclass(frozen=True, slots=True)
class TokenDef:
    """One registry entry (ADR 022 D-022-02). ``validator`` is the dotted import
    path to a pure ``validate_<token>`` callable; ``resolve_validator`` loads it."""

    name: str
    base_python: str
    json_form: str
    validator: str
    min_protocol_version: str
    introduced_by: str
    rationale: str
    json_schema_ref: str | None = None
    deprecated_in: str | None = None


# Lazily-populated process registry. None until first access; load_registry()
# fills it from the packaged default and returns the live dict so register_token
# is visible to subsequent get_token / load_registry calls.
_REGISTRY: dict[str, TokenDef] | None = None


def load_registry(path: str | Path | None = None) -> dict[str, TokenDef]:
    """Return the token registry as ``{name: TokenDef}``.

    With no ``path``, return the live process registry (lazily loading the
    packaged 12-token default on first call). With a ``path``, parse THAT file
    and return a fresh dict without touching process state -- the seam tests use
    to load a minimal or deliberately broken registry in isolation.
    """
    global _REGISTRY
    if path is not None:
        return _parse_registry_file(Path(path))
    if _REGISTRY is None:
        _REGISTRY = _parse_registry_file(_PACKAGED_REGISTRY_PATH)
    return _REGISTRY


def register_token(token: TokenDef) -> None:
    """Add (or override) ``token`` in the live process registry -- the MINOR
    protocol extension path (D-022-04). Ensures the default is loaded first so a
    registration augments the 12 v1 tokens rather than replacing them.

    Overriding an ALREADY-registered name -- including one of the 12 core v1
    tokens -- is permitted (that is the point of the extension path) but is
    NEVER silent: it is logged at WARN, matching the sibling
    ``mcp.registry.register_tool`` clobber contract (R-227 / Article V:
    observable, no silent state change)."""
    registry = load_registry()
    existing = registry.get(token.name)
    if existing is not None:
        _logger.warning(
            "register_token: clobbering already-registered type token %r "
            "(introduced_by %r -> %r)",
            token.name,
            existing.introduced_by,
            token.introduced_by,
        )
    registry[token.name] = token


def get_token(name: str) -> TokenDef:
    """Return the ``TokenDef`` for ``name`` from the live registry, raising
    ``UnknownTypeTokenError`` if it is not registered (parity with the W2
    ``parse_type`` contract for an unknown token)."""
    token = load_registry().get(name)
    if token is None:
        raise UnknownTypeTokenError(f"unknown type token: {name!r}")
    return token


def resolve_validator(token: TokenDef) -> Callable[..., bool]:
    """Import and return the validator callable named by ``token.validator``.

    Raises if the module or attribute does not exist -- the D-022-02 startup
    contract ("a runtime that fails to load any registered validator MUST refuse
    to freeze any artifact"). The caller decides how to surface that refusal.
    """
    module_path, _, attr = token.validator.rpartition(".")
    if not module_path:
        raise OpenVarError(f"validator path is not dotted: {token.validator!r}")
    module = importlib.import_module(module_path)
    return getattr(module, attr)


def reset_registry() -> None:
    """Drop the cached process registry so the next access reloads the packaged
    default. The test-isolation seam (conftest autouse) -- never needed in
    production, where the registry is loaded once at startup."""
    global _REGISTRY
    _REGISTRY = None


# --------------------------------------------------------------------------- #
# parsing + validation                                                          #
# --------------------------------------------------------------------------- #
def _parse_registry_file(path: Path) -> dict[str, TokenDef]:
    if _yaml is None:  # pragma: no cover - yaml is present in the repo env
        raise OpenVarError(
            f"PyYAML is required to load the type registry ({path}): {_YAML_IMPORT_ERROR}"
        )
    try:
        raw = _yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise OpenVarError(f"cannot read type registry {path}: {exc}") from exc
    except _yaml.YAMLError as exc:
        raise ValueError(f"type registry {path} is not valid YAML: {exc}") from exc

    if not isinstance(raw, dict) or "tokens" not in raw:
        raise ValueError(f"type registry {path} must have a top-level 'tokens:' list")
    entries = raw["tokens"]
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"type registry {path} 'tokens' must be a non-empty list")

    registry: dict[str, TokenDef] = {}
    for index, entry in enumerate(entries):
        token = _token_def_from_entry(entry, index, path)
        if token.name in registry:
            raise ValueError(f"type registry {path}: duplicate token name {token.name!r}")
        registry[token.name] = token
    return registry


def _token_def_from_entry(entry: Any, index: int, path: Path) -> TokenDef:
    if not isinstance(entry, dict):
        raise ValueError(f"type registry {path}: token #{index} is not a mapping")
    for field in _REQUIRED_FIELDS:
        if not entry.get(field):
            raise ValueError(
                f"type registry {path}: token #{index} is missing required field {field!r}"
            )
    json_form = entry["json_form"]
    if json_form not in _VALID_JSON_FORMS:
        raise ValueError(
            f"type registry {path}: token {entry['name']!r} has invalid json_form {json_form!r}"
        )
    return TokenDef(
        name=entry["name"],
        base_python=entry["base_python"],
        json_form=json_form,
        validator=entry["validator"],
        min_protocol_version=str(entry["min_protocol_version"]),
        introduced_by=entry["introduced_by"],
        rationale=entry["rationale"],
        json_schema_ref=entry.get("json_schema_ref"),
        deprecated_in=entry.get("deprecated_in"),
    )
