"""Wire format -- serialize a frozen artifact to JSON for cross-runtime transfer
and deserialize it back (spec S 5, ADR 022 D-022-04).

A frozen artifact is a self-contained Lego piece: ``meta`` (protocol + version +
provenance), ``frontmatter`` (kind, id, version, ``_open_vars_frozen``,
``_filled_vars``), ``open_vars_declarations``, and ``body``. ``serialize_artifact``
validates the piece is frozen and well-formed, then emits JSON;
``deserialize_artifact`` parses, enforces the receiving protocol (S 5.2), and
returns the dict. The two are exact inverses for JSON-native data -- the SC-004
invariant ``deserialize(serialize(x)) == x`` holds for every one of the 12 token
types (their filled values are all JSON-native: str/int/float/bool/list/dict).

Version policy (D-022-04 / S 5.3): a 1.x runtime accepts any ``1.y`` blob (minor
versions are additive) and refuses ``>= 2.0`` with ``UnsupportedProtocolVersionError``.
Every other structural defect -- unparseable JSON, a missing top-level key
(FR-015), the wrong protocol name, an unparseable version, or an unfrozen
artifact -- raises ``MalformedWireFormatError``.

This layer does NOT re-validate filled values against their declarations: freeze
already did that (spec S 3 Stage 3), and re-validation would couple deserialize
to a kind resolver, breaking the offline-portable contract (Art. XIV).

Spec provenance: cexai-specs/_revisions/spec_open_variables_protocol.md (S 5.1,
S 5.2, S 5.3, FR-015, SC-004) + cexai-specs/_decisions/adr_022_open_variables_full_protocol.md
(D-022-04).

absorbs: cexai-specs/open-variables-protocol
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from cexai.foundation.open_vars.errors import (
    MalformedWireFormatError,
    UnsupportedProtocolVersionError,
)

__all__ = [
    "PROTOCOL",
    "PROTOCOL_VERSION",
    "SUPPORTED_MAJOR_VERSION",
    "serialize_artifact",
    "deserialize_artifact",
]

PROTOCOL = "cexai-open-vars"
PROTOCOL_VERSION = "1.0"
SUPPORTED_MAJOR_VERSION = 1

# The S 5.1 top-level keys. Missing any one is a MalformedWireFormatError (FR-015).
_TOP_LEVEL_KEYS: tuple[str, ...] = ("meta", "frontmatter", "open_vars_declarations", "body")


def serialize_artifact(frozen: Mapping[str, Any]) -> str:
    """Serialize a frozen artifact to the canonical JSON wire format (S 5.1).

    Validates the artifact is structurally complete, carries the right protocol,
    and is actually frozen (``frontmatter._open_vars_frozen is True``) -- a
    template cannot be transferred. Does not mutate ``frozen``. Raises
    ``MalformedWireFormatError`` on any structural defect.
    """
    _require_wire_shape(frozen)
    _require_protocol_name(frozen["meta"])
    _require_frozen(frozen["frontmatter"])
    return json.dumps(frozen, ensure_ascii=False)


def deserialize_artifact(blob: str) -> dict[str, Any]:
    """Deserialize a JSON wire blob back to a frozen-artifact dict (S 5.2).

    Enforces, in order: parseable JSON; the four top-level keys; the
    ``cexai-open-vars`` protocol name; a supported ``protocol_version`` (1.x ok,
    ``>= 2.0`` -> ``UnsupportedProtocolVersionError``); and ``_open_vars_frozen
    is True``. Returns the parsed dict unchanged so ``deserialize(serialize(x))
    == x``.
    """
    try:
        parsed = json.loads(blob)
    except (json.JSONDecodeError, TypeError) as exc:
        raise MalformedWireFormatError(f"wire blob is not valid JSON: {exc}") from exc
    _require_wire_shape(parsed)
    meta = parsed["meta"]
    _require_protocol_name(meta)
    _check_protocol_version(meta)
    _require_frozen(parsed["frontmatter"])
    return parsed


# --------------------------------------------------------------------------- #
# structural + protocol guards                                                  #
# --------------------------------------------------------------------------- #
def _require_wire_shape(artifact: Any) -> None:
    if not isinstance(artifact, Mapping):
        raise MalformedWireFormatError(
            f"wire artifact must be a mapping, got {type(artifact).__name__}"
        )
    missing = [key for key in _TOP_LEVEL_KEYS if key not in artifact]
    if missing:
        raise MalformedWireFormatError(f"wire artifact is missing top-level key(s): {missing}")
    if not isinstance(artifact["meta"], Mapping):
        raise MalformedWireFormatError("wire 'meta' must be a mapping")
    if not isinstance(artifact["frontmatter"], Mapping):
        raise MalformedWireFormatError("wire 'frontmatter' must be a mapping")


def _require_protocol_name(meta: Mapping[str, Any]) -> None:
    protocol = meta.get("protocol")
    if protocol != PROTOCOL:
        raise MalformedWireFormatError(
            f"unexpected protocol {protocol!r} (expected {PROTOCOL!r})"
        )


def _check_protocol_version(meta: Mapping[str, Any]) -> None:
    raw = meta.get("protocol_version")
    major = _major_of(raw)
    if major > SUPPORTED_MAJOR_VERSION:
        raise UnsupportedProtocolVersionError(
            f"protocol_version {raw!r} is not supported by this {PROTOCOL_VERSION} runtime "
            f"(major {major} > {SUPPORTED_MAJOR_VERSION})"
        )


def _major_of(raw: Any) -> int:
    if not isinstance(raw, str) or not raw:
        raise MalformedWireFormatError(f"protocol_version must be a version string, got {raw!r}")
    head = raw.split(".", 1)[0]
    try:
        return int(head)
    except ValueError as exc:
        raise MalformedWireFormatError(f"unparseable protocol_version {raw!r}") from exc


def _require_frozen(frontmatter: Mapping[str, Any]) -> None:
    if frontmatter.get("_open_vars_frozen") is not True:
        raise MalformedWireFormatError(
            "artifact is not frozen (_open_vars_frozen must be true to transfer)"
        )
