"""Pure, per-token validators + the validate_open_var orchestrator.

Each ``validate_<token>(value, *, constraints=None, **ctx) -> bool`` is PURE: no
I/O, no global state, no clock -- the same value validates identically on every
runtime (ADR 022 D-022-02 validator contract). A valid value returns ``True``; an
invalid one raises the specific open_vars error. ``validate_open_var`` dispatches
on a parsed ``OpenVar`` declaration, threading constraints, enum membership, the
list element type, and an injected kind resolver.

kind_ref stays pure by taking an injected ``kind_resolver`` callable or a
``known_kinds`` set rather than reading ``.cex/kinds_meta.json`` itself (handoff).
When NEITHER is injected, existence cannot be checked at all -- kind_ref raises
``KindExistenceUnverifiedError`` rather than returning a format-only ``True`` that
would read as a verified PASS (R-228 / f7-honesty). The W3 wire layer supplies
the real kinds_meta.json resolver for the checked path.
``json_schema`` guards its optional ``jsonschema`` import so the other 11 tokens
validate even if it is absent (handoff IF BLOCKED).

Spec provenance: cexai-specs/_revisions/spec_open_variables_protocol.md (S 2.2,
US P4, FR-008/FR-010) + cexai-specs/_decisions/adr_022_open_variables_full_protocol.md
(D-022-01 validation contracts, D-022-02 purity).

absorbs: cexai-specs/open-variables-protocol
"""

from __future__ import annotations

import datetime as _dt
import re
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from cexai.foundation.open_vars import registry as _registry
from cexai.foundation.open_vars.errors import (
    ConstraintViolationError,
    InvalidEnumValueError,
    KindExistenceUnverifiedError,
    OpenVarError,
    TypeMismatchError,
)
from cexai.foundation.open_vars.schema import OpenVar, parse_type

try:  # optional: only the json_schema token needs it (handoff IF BLOCKED).
    import jsonschema as _jsonschema
except ImportError:  # pragma: no cover - jsonschema is a declared test/runtime dep
    _jsonschema = None

__all__ = [
    "validate_str",
    "validate_int",
    "validate_float",
    "validate_bool",
    "validate_enum",
    "validate_kind_ref",
    "validate_list",
    "validate_dict",
    "validate_url",
    "validate_iso_date",
    "validate_iso_datetime",
    "validate_json_schema",
    "validate_open_var",
    "TOKEN_VALIDATORS",
]

# host present after scheme, no whitespace; optional port/path/query/fragment.
_URL_RE = re.compile(r"^https?://[^/\s:@]+(:\d+)?(/[^\s]*)?$")
_URL_MAX = 2048


# --------------------------------------------------------------------------- #
# Constraint helpers                                                            #
# --------------------------------------------------------------------------- #
def _as_constraints(constraints: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return constraints or {}


def _check_range(value: float, constraints: Mapping[str, Any]) -> None:
    minimum = constraints.get("minimum")
    maximum = constraints.get("maximum")
    if minimum is not None and value < minimum:
        raise ConstraintViolationError(f"{value} is below minimum {minimum}")
    if maximum is not None and value > maximum:
        raise ConstraintViolationError(f"{value} is above maximum {maximum}")


def _check_size(length: int, constraints: Mapping[str, Any], *, min_key: str, max_key: str) -> None:
    minimum = constraints.get(min_key)
    maximum = constraints.get(max_key)
    if minimum is not None and length < minimum:
        raise ConstraintViolationError(f"size {length} is below {min_key} {minimum}")
    if maximum is not None and length > maximum:
        raise ConstraintViolationError(f"size {length} is above {max_key} {maximum}")


# --------------------------------------------------------------------------- #
# Base tokens (8)                                                               #
# --------------------------------------------------------------------------- #
def validate_str(value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any) -> bool:
    if not isinstance(value, str):
        raise TypeMismatchError(f"expected str, got {type(value).__name__}")
    c = _as_constraints(constraints)
    _check_size(len(value), c, min_key="min_length", max_key="max_length")
    pattern = c.get("pattern")
    if pattern is not None:
        try:
            matched = re.search(pattern, value)
        except re.error as exc:
            raise ConstraintViolationError(f"invalid pattern {pattern!r}: {exc}") from exc
        if matched is None:
            raise ConstraintViolationError(f"{value!r} does not match pattern {pattern!r}")
    return True


def validate_int(value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeMismatchError(f"expected int, got {type(value).__name__}")
    _check_range(value, _as_constraints(constraints))
    return True


def validate_float(value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any) -> bool:
    # int is an acceptable JSON number for a float slot; bool is not.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeMismatchError(f"expected float, got {type(value).__name__}")
    _check_range(float(value), _as_constraints(constraints))
    return True


def validate_bool(value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any) -> bool:
    if not isinstance(value, bool):
        raise TypeMismatchError(f"expected bool, got {type(value).__name__}")
    return True


def validate_enum(
    value: Any,
    *,
    constraints: Mapping[str, Any] | None = None,
    allowed_values: Iterable[str] | None = None,
    **ctx: Any,
) -> bool:
    if not allowed_values:
        raise InvalidEnumValueError("enum validation requires a non-empty allowed_values")
    if value not in list(allowed_values):
        raise InvalidEnumValueError(f"{value!r} is not one of {list(allowed_values)!r}")
    return True


def validate_kind_ref(
    value: Any,
    *,
    constraints: Mapping[str, Any] | None = None,
    kind_resolver: Callable[[str], bool] | None = None,
    known_kinds: Iterable[str] | None = None,
    **ctx: Any,
) -> bool:
    if not isinstance(value, str):
        raise TypeMismatchError(f"expected str kind_ref, got {type(value).__name__}")
    if not value.startswith("kind:"):
        raise ConstraintViolationError("kind_ref must use the 'kind:' prefix")
    target = value[len("kind:"):]
    if not target:
        raise ConstraintViolationError("kind_ref target is empty")
    if kind_resolver is not None:
        if not kind_resolver(target):
            raise ConstraintViolationError(f"unknown kind_ref target: {target!r}")
        return True
    if known_kinds is not None:
        if target not in set(known_kinds):
            raise ConstraintViolationError(f"unknown kind_ref target: {target!r}")
        return True
    # No resolver injected: the 'kind:' format is well-formed, but existence was
    # NEVER checked. Returning True here would read to the caller as "this kind
    # exists" -- a false PASS (R-228 / f7-honesty). Raise instead so an
    # un-checkable kind_ref is never silently accepted; a caller that genuinely
    # wants offline format-only validation must catch this specific error.
    raise KindExistenceUnverifiedError(
        f"kind_ref {value!r} has valid format but existence of {target!r} is "
        "UNVERIFIED: no kind_resolver or known_kinds was injected"
    )


def validate_list(
    value: Any,
    *,
    constraints: Mapping[str, Any] | None = None,
    element_type: str | None = None,
    **ctx: Any,
) -> bool:
    if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, (list, tuple)):
        raise TypeMismatchError(f"expected list, got {type(value).__name__}")
    _check_size(len(value), _as_constraints(constraints), min_key="min_items", max_key="max_items")
    if element_type:
        element_validator = TOKEN_VALIDATORS.get(element_type)
        if element_validator is None:  # defensive: parse_type already vets this
            raise TypeMismatchError(f"unsupported list element type: {element_type!r}")
        for item in value:
            element_validator(item, **ctx)
    return True


def validate_dict(value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any) -> bool:
    if not isinstance(value, Mapping):
        raise TypeMismatchError(f"expected dict, got {type(value).__name__}")
    # schema_ref (a JSON Schema URI) resolution is out of v1 scope (ADR 022).
    return True


# --------------------------------------------------------------------------- #
# Custom tokens (4) -- ADR 022 D-022-01                                          #
# --------------------------------------------------------------------------- #
def validate_url(value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any) -> bool:
    if not isinstance(value, str):
        raise TypeMismatchError(f"expected url str, got {type(value).__name__}")
    if len(value) > _URL_MAX:
        raise ConstraintViolationError(f"url exceeds {_URL_MAX} chars ({len(value)})")
    if _URL_RE.match(value) is None:
        raise TypeMismatchError(f"{value!r} is not a valid http(s) url")
    return True


def validate_iso_date(value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any) -> bool:
    if not isinstance(value, str):
        raise TypeMismatchError(f"expected iso_date str, got {type(value).__name__}")
    try:
        _dt.date.fromisoformat(value)
    except ValueError as exc:
        raise TypeMismatchError(f"{value!r} is not an ISO date (YYYY-MM-DD): {exc}") from exc
    return True


def validate_iso_datetime(
    value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any
) -> bool:
    if not isinstance(value, str):
        raise TypeMismatchError(f"expected iso_datetime str, got {type(value).__name__}")
    try:
        parsed = _dt.datetime.fromisoformat(value)
    except ValueError as exc:
        raise TypeMismatchError(f"{value!r} is not an ISO 8601 datetime: {exc}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ConstraintViolationError(f"{value!r} must be timezone-aware")
    return True


def validate_json_schema(
    value: Any, *, constraints: Mapping[str, Any] | None = None, **ctx: Any
) -> bool:
    if not isinstance(value, Mapping):
        raise TypeMismatchError(f"expected a JSON Schema object, got {type(value).__name__}")
    if _jsonschema is None:  # pragma: no cover - dependency is declared
        raise OpenVarError("json_schema validation unavailable: jsonschema not installed")
    try:
        _jsonschema.Draft202012Validator.check_schema(dict(value))
    except _jsonschema.exceptions.SchemaError as exc:
        raise TypeMismatchError(f"invalid JSON Schema: {exc.message}") from exc
    return True


# Dispatch table -- keyed by canonical token name (``list[T]`` is the family).
TOKEN_VALIDATORS: dict[str, Callable[..., bool]] = {
    "str": validate_str,
    "int": validate_int,
    "float": validate_float,
    "bool": validate_bool,
    "enum": validate_enum,
    "kind_ref": validate_kind_ref,
    "list[T]": validate_list,
    "dict": validate_dict,
    "url": validate_url,
    "iso_date": validate_iso_date,
    "iso_datetime": validate_iso_datetime,
    "json_schema": validate_json_schema,
}


# --------------------------------------------------------------------------- #
# Orchestrator                                                                  #
# --------------------------------------------------------------------------- #
def validate_open_var(
    declaration: OpenVar,
    value: Any,
    *,
    kind_resolver: Callable[[str], bool] | None = None,
    known_kinds: Iterable[str] | None = None,
) -> bool:
    """Validate ``value`` against a parsed ``OpenVar`` declaration.

    Dispatches on ``declaration.type`` (normalized via ``parse_type``), then
    applies the declaration's ``constraints``, enum ``allowed_values``, and -- for
    a ``list[T]`` -- the element type. ``kind_ref`` resolution uses the injected
    ``kind_resolver`` / ``known_kinds``. Pure + deterministic: returns ``True`` or
    raises the specific open_vars error.

    ``token_name`` is normally one of the 12 hardcoded ``TOKEN_VALIDATORS`` keys.
    When it is not, ``parse_type`` accepted it only because it is registered in
    the live type registry (a MINOR-extension token added via ``register_token``,
    ADR 022 D-022-04) -- resolve and use ITS declared validator so the extension
    path actually validates instead of having no dispatch entry (R-218).
    """
    token_name, element_type = parse_type(declaration.type)
    validator = TOKEN_VALIDATORS.get(token_name)
    if validator is None:
        validator = _registry.resolve_validator(_registry.get_token(token_name))
    return validator(
        value,
        constraints=declaration.constraints,
        allowed_values=declaration.allowed_values,
        element_type=element_type,
        kind_resolver=kind_resolver,
        known_kinds=known_kinds,
    )
