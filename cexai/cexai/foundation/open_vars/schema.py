"""The OpenVar declaration schema -- 12 typed fields, 3 closed-vocabulary enums,
and the closed v1 set of 12 type tokens.

This is the KEYSTONE of CEXAI governance (Article XIX): every parameterizable
artifact field is declared here as a typed late-binding slot rather than
hardcoded. ``parse_open_var`` is the GOVERNED entry point -- it turns a raw
frontmatter dict into a validated, frozen ``OpenVar`` or raises a specific
error from the open_vars vocabulary.

pydantic v2 is the right tool here (declarative field validation + coercion of
the three enums); the frozen-dataclass contracts in ``_shared/types.py`` cover
the hot LLM path instead. The two choices are deliberate and complementary.

Spec provenance: cexai-specs/_revisions/spec_open_variables_protocol.md (S 2.2,
S 2.3, FR-002..FR-011) + cexai-specs/_decisions/adr_022_open_variables_full_protocol.md
(D-022-01 token set, D-022-05 field 12 ``rebind_allowed``).

absorbs: cexai-specs/open-variables-protocol
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any

import pydantic
from pydantic import BaseModel, ConfigDict, Field

from cexai.foundation.open_vars import registry as _registry
from cexai.foundation.open_vars.errors import (
    InvalidStrategyError,
    MalformedOpenVarError,
    UnknownTypeTokenError,
)

__all__ = [
    "FillerRole",
    "FillerStage",
    "FillerStrategy",
    "TypeToken",
    "TYPE_TOKENS",
    "OpenVar",
    "parse_open_var",
    "parse_type",
]

# snake_case slug for ``name`` (spec S 2.3 Field 1): lowercase, digit, underscore;
# must start with a letter.
_SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")

# A parametrized list type, e.g. ``list[str]`` -> element token ``str``.
_LIST_RE = re.compile(r"^list\[(.+)\]$")


# --------------------------------------------------------------------------- #
# Closed-vocabulary enums (spec FR-004, FR-005, FR-011)                          #
# --------------------------------------------------------------------------- #
class FillerRole(str, Enum):
    """Which actor fills the variable (spec Field 4 / FR-004)."""

    COMPILER = "compiler"
    N01 = "n01"
    N02 = "n02"
    N03 = "n03"
    N04 = "n04"
    N05 = "n05"
    N06 = "n06"
    N07 = "n07"
    USER = "user"


class FillerStage(str, Enum):
    """The 8F stage at which filling occurs (spec Field 5 / FR-005). F1..F6 only:
    F7 GOVERN validates and F8 COLLABORATE persists -- neither fills."""

    F1_CONSTRAIN = "F1_CONSTRAIN"
    F2_BECOME = "F2_BECOME"
    F3_INJECT = "F3_INJECT"
    F4_REASON = "F4_REASON"
    F5_CALL = "F5_CALL"
    F6_PRODUCE = "F6_PRODUCE"


class FillerStrategy(str, Enum):
    """Fallback when context_hints are exhausted (spec Field 9 / FR-011)."""

    USE_FIRST_CONTEXT_HINT = "use_first_context_hint"
    GDP_ASK = "gdp_ask"
    USE_DEFAULT_VALUE = "use_default_value"
    BLOCK = "block"


# --------------------------------------------------------------------------- #
# Type-token registry (closed v1 set -- ADR 022 D-022-01)                        #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class TypeToken:
    """One entry in the closed v1 token set. ``constraint_keys`` are the keys the
    matching ``validate_<token>`` honors in a declaration's ``constraints`` dict;
    any other key is ignored (spec FR-010)."""

    name: str
    category: str  # "base" (8) | "custom" (4)
    json_form: str  # string | integer | number | boolean | array | object
    constraint_keys: tuple[str, ...]


def _token(name: str, category: str, json_form: str, *constraint_keys: str) -> tuple[str, TypeToken]:
    return name, TypeToken(name, category, json_form, tuple(constraint_keys))


# The 12 tokens. ``list[T]`` is keyed by its family name; concrete declarations
# (``list[str]``) are normalized by ``parse_type``.
TYPE_TOKENS: Mapping[str, TypeToken] = MappingProxyType(
    dict(
        [
            _token("str", "base", "string", "min_length", "max_length", "pattern"),
            _token("int", "base", "integer", "minimum", "maximum"),
            _token("float", "base", "number", "minimum", "maximum"),
            _token("bool", "base", "boolean"),
            _token("enum", "base", "string"),
            _token("kind_ref", "base", "string"),
            _token("list[T]", "base", "array", "min_items", "max_items"),
            _token("dict", "base", "object", "schema_ref"),
            _token("url", "custom", "string"),
            _token("iso_date", "custom", "string"),
            _token("iso_datetime", "custom", "string"),
            _token("json_schema", "custom", "object"),
        ]
    )
)

# Tokens permitted as the element of a ``list[T]``: everything except ``enum``
# (needs per-element allowed_values) and a nested list (v1 has no nested lists).
_ELEMENT_TOKENS: frozenset[str] = frozenset(TYPE_TOKENS) - {"enum", "list[T]"}


def parse_type(type_str: str) -> tuple[str, str | None]:
    """Normalize a declared ``type`` value to ``(token_name, element_type)``.

    A scalar token returns ``(token, None)``. A list returns
    ``("list[T]", element_token_or_None)`` -- bare ``list`` is an untyped list.
    Raises ``UnknownTypeTokenError`` for any token outside the closed v1 set AND
    not present in the live type registry, or for a ``list[T]`` whose element
    token is unknown or unsupported.

    A scalar token not in the hardcoded ``TYPE_TOKENS`` set falls back to the
    live process registry (``registry.get_token``) so a token added via
    ``register_token`` -- the documented MINOR-version extension path, ADR 022
    D-022-04 -- is actually recognized here rather than only existing in an
    unconsulted registry (R-218).
    """
    if type_str == "list" or type_str == "list[T]":
        return "list[T]", None
    match = _LIST_RE.match(type_str)
    if match:
        element = match.group(1).strip()
        if element not in _ELEMENT_TOKENS:
            raise UnknownTypeTokenError(
                f"list element type {element!r} is not a supported v1 token"
            )
        return "list[T]", element
    if type_str in TYPE_TOKENS:
        return type_str, None
    if _is_registered_extension_token(type_str):
        return type_str, None
    raise UnknownTypeTokenError(f"unknown type token: {type_str!r}")


def _is_registered_extension_token(name: str) -> bool:
    """True when ``name`` is registered in the live type registry (whether one of
    the 12 packaged defaults or a MINOR-extension token added via
    ``register_token``). Only called for names already known NOT to be in the
    hardcoded ``TYPE_TOKENS`` set, so in practice this reports extension tokens."""
    try:
        _registry.get_token(name)
    except UnknownTypeTokenError:
        return False
    return True


# --------------------------------------------------------------------------- #
# The 12-field declaration model                                                #
# --------------------------------------------------------------------------- #
class OpenVar(BaseModel):
    """A typed late-binding slot declared in an artifact's frontmatter (the
    Article XIX primitive). Construct via ``parse_open_var`` for governed errors;
    direct construction enforces the same rules but surfaces pydantic's native
    ``ValidationError`` for structural problems."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    type: str
    description: str
    filler_role: FillerRole
    filler_stage: FillerStage
    allowed_values: list[str] | None = None
    context_hints: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    default_filler_strategy: FillerStrategy
    required: bool = True
    default_value: Any = None
    rebind_allowed: bool = False

    @pydantic.model_validator(mode="after")
    def _govern(self) -> OpenVar:
        # 1. name discipline (snake_case slug).
        if not _SNAKE_CASE.match(self.name):
            raise MalformedOpenVarError(f"name {self.name!r} is not snake_case")

        # 2. type token validity (raises UnknownTypeTokenError).
        token_name, _ = parse_type(self.type)

        # 3. enum <-> allowed_values coupling (spec Field 6 / FR-008).
        if token_name == "enum":
            if not self.allowed_values:
                raise MalformedOpenVarError("enum type requires a non-empty allowed_values")
        elif self.allowed_values is not None:
            raise MalformedOpenVarError(
                f"allowed_values is only valid for enum, not {self.type!r}"
            )

        # 4. default_value <-> required coupling (spec Field 11).
        if self.required and self.default_value is not None:
            raise MalformedOpenVarError("default_value must be null when required is true")

        # 5. use_default_value strategy gate (spec FR-011) -> InvalidStrategyError.
        if self.default_filler_strategy is FillerStrategy.USE_DEFAULT_VALUE:
            if self.required:
                raise InvalidStrategyError("use_default_value is invalid on a required variable")
            if self.default_value is None:
                raise InvalidStrategyError("use_default_value requires a non-null default_value")

        return self


def parse_open_var(declaration: Mapping[str, Any]) -> OpenVar:
    """Build an ``OpenVar`` from a raw frontmatter mapping -- the GOVERNED entry.

    Structural failures (missing required field, unknown extra field, wrong field
    type, bad enum value) become ``MalformedOpenVarError``. Semantic failures
    raised inside the model (``UnknownTypeTokenError`` for a bad token,
    ``InvalidStrategyError`` for a misused strategy) propagate as themselves.
    """
    try:
        return OpenVar(**dict(declaration))
    except pydantic.ValidationError as exc:
        raise MalformedOpenVarError(_summarize(exc)) from exc


def _summarize(exc: pydantic.ValidationError) -> str:
    """Compact, ASCII-safe one-line summary of a pydantic validation failure."""
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", ())) or "<root>"
        parts.append(f"{loc}: {err.get('msg', 'invalid')}")
    return "; ".join(parts) or "malformed open_var declaration"
