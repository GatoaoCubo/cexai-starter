"""The six-slot open_var contract -- the factory's net-new layer (Mode B).

This module is the PRODUCT. MoneyPrinterTurbo already renders topic -> mp4; the one
net-new thing cexai adds is a typed ``{brand}``-fillable contract so ANY brand fills
six slots and gets its own branded short video with ZERO code change (SC-008). The
contract is the runtime projection of two existing kinds (ZERO new kinds, per the
v0.6 taxonomy ADR):

  * ``input_schema``      -- the typed SHAPE: the six slots, their types, which are
                             required, and their defaults (``OPEN_VAR_SLOTS`` +
                             ``BrandProfile``).
  * ``validation_schema`` -- the GATE: required-slot enforcement + the
                             ``{video_style}`` enum gate (Article XIX HARD FAIL).

Rather than reinvent that machinery, ``fill`` REUSES the foundation open_vars
validator (``cexai.foundation.open_vars``) -- the canonical Article XIX
implementation: each slot is declared as a governed ``OpenVar`` (``parse_open_var``)
and each filled value is checked with ``validate_open_var``. The spec's semantic
``audio_path`` type maps to the closed ``str`` token (a path string); the spec's
``operator`` filler-role maps to the canonical ``user`` role.

Mapping of the six slots to the foundation declaration (spec frontmatter + S 3.3):

| slot         | token | required | default      | filler   | stage         |
|--------------|-------|----------|--------------|----------|---------------|
| brand        | str   | yes      | --           | user     | F1_CONSTRAIN  |
| niche        | str   | yes      | --           | user     | F1_CONSTRAIN  |
| topic        | str   | yes      | --           | user     | F4_REASON     |
| brand_voice  | str   | no       | null         | user     | F3_INJECT     |
| video_style  | enum  | no       | educational  | user     | F1_CONSTRAIN  |
| language     | str   | no       | pt-BR        | compiler | F1_CONSTRAIN  |

absorbs: 20_content_factory
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from cexai.content_factory._shared.errors import OpenVarValidationError
from cexai.content_factory._shared.types import OPEN_VAR_SLOTS, BrandProfile
from cexai.foundation.open_vars.errors import OpenVarError
from cexai.foundation.open_vars.schema import OpenVar, parse_open_var
from cexai.foundation.open_vars.validators import validate_open_var

__all__ = ["OPEN_VAR_SLOTS", "fill", "declarations"]

# The six slot declarations, as raw frontmatter mappings parsed into governed
# ``OpenVar`` objects at import time. ``required`` slots omit ``default_value`` (the
# model requires it null when required); the two ``use_default_value`` strategies are
# valid only on optional slots with a non-null default (video_style / language), so
# the optional-but-null ``brand_voice`` uses ``gdp_ask``.
_RAW_DECLARATIONS: tuple[Mapping[str, Any], ...] = (
    {
        "name": "brand",
        "type": "str",
        "description": "Brand identity injected into the script prompt + endcard overlay.",
        "filler_role": "user",
        "filler_stage": "F1_CONSTRAIN",
        "default_filler_strategy": "block",
        "required": True,
    },
    {
        "name": "niche",
        "type": "str",
        "description": "Content domain; filters the script topic + seeds Pexels search terms.",
        "filler_role": "user",
        "filler_stage": "F1_CONSTRAIN",
        "default_filler_strategy": "block",
        "required": True,
    },
    {
        "name": "topic",
        "type": "str",
        "description": "The single video subject (the MPT video_subject).",
        "filler_role": "user",
        "filler_stage": "F4_REASON",
        "default_filler_strategy": "block",
        "required": True,
    },
    {
        "name": "brand_voice",
        "type": "str",
        "description": "Reference audio path (>=5s) for the Chatterbox zero-shot clone; null -> neutral voice.",
        "filler_role": "user",
        "filler_stage": "F3_INJECT",
        "default_filler_strategy": "gdp_ask",
        "required": False,
        "default_value": None,
    },
    {
        "name": "video_style",
        "type": "enum",
        "allowed_values": ["educational", "narrative", "listicle"],
        "description": "Script tone + subtitle/font preset + clip-concat mode.",
        "filler_role": "user",
        "filler_stage": "F1_CONSTRAIN",
        "default_filler_strategy": "use_default_value",
        "required": False,
        "default_value": "educational",
    },
    {
        "name": "language",
        "type": "str",
        "description": "Narration + script locale (BCP-47).",
        "filler_role": "compiler",
        "filler_stage": "F1_CONSTRAIN",
        "default_filler_strategy": "use_default_value",
        "required": False,
        "default_value": "pt-BR",
    },
)

# Parsed once -- a malformed declaration here is a build-time error, not a runtime one.
_DECLARATIONS: tuple[OpenVar, ...] = tuple(parse_open_var(d) for d in _RAW_DECLARATIONS)


def declarations() -> tuple[OpenVar, ...]:
    """The six governed ``OpenVar`` slot declarations (the ``input_schema`` shape),
    in the spec's frontmatter order. Read-only; useful for surfacing the contract to
    a CLI ``--help`` or a GDP prompt."""
    return _DECLARATIONS


def fill(values: Mapping[str, Any]) -> BrandProfile:
    """Fill + validate the six open_var slots into a typed ``BrandProfile``.

    This is the ``validation_schema`` gate (Article XIX). For each declared slot:
      * present (non-null) value -> validated via the foundation ``validate_open_var``
        (type check + the ``{video_style}`` enum gate); an invalid value raises
        ``OpenVarValidationError``.
      * absent REQUIRED slot (``brand`` / ``niche`` / ``topic``) -> collected and
        raised as a single ``OpenVarValidationError`` naming every missing slot (the
        pre-render HARD FAIL, FR-003).
      * absent OPTIONAL slot -> its declared default is applied (``video_style`` ->
        ``educational``, ``language`` -> ``pt-BR``, ``brand_voice`` -> ``None``).

    Returns a frozen ``BrandProfile`` carrying all six resolved slots.
    """
    resolved: dict[str, Any] = {}
    missing: list[str] = []

    for decl in _DECLARATIONS:
        name = decl.name
        if name in values and values[name] is not None:
            value = values[name]
            try:
                validate_open_var(decl, value)
            except OpenVarError as exc:
                raise OpenVarValidationError(
                    f"open_var slot {name!r} failed validation: {exc}"
                ) from exc
            resolved[name] = value
        elif decl.required:
            missing.append(name)
        else:
            resolved[name] = decl.default_value

    if missing:
        raise OpenVarValidationError(
            f"missing required open_var slot(s): {missing}",
            missing_fields=tuple(missing),
        )

    return BrandProfile(**resolved)
