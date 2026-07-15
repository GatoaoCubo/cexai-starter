"""Discovery + version-range semantics for declared MCP extensions (W2).

``discover_extensions`` turns a feature's declared dependency list (plain dicts,
the portable on-disk form) into validated, immutable ``ExtensionSpec`` records.
``version_satisfies`` interprets a declared semver range against a server's
reported version -- a small, dependency-free matcher (Article VIII: no new
runtime dependency for a leaf utility) covering the forms a feature config
actually uses: ``*`` / exact / caret / tilde / comparator-list.

``mcp_extension`` is NOT a new CEX kind -- it EXTENDS the canonical ``mcp_server``
kind by three attributes (name, version_range, transport). Kind registration is
W4, not here.

Spec provenance: cexai-specs/08_goose/spec.md (FR-004, P2 version-mismatch edge).

absorbs: 08_goose/mcp-extension-loader
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cexai.foundation.mcp.errors import McpExtensionLoadError

__all__ = [
    "ExtensionSpec",
    "discover_extensions",
    "version_satisfies",
    "VALID_TRANSPORTS",
]

# The two MCP transports CEXAI commits to in v0.1 (Principle GO2). The SDK also
# exposes SSE, but streamable-http supersedes it; keep the surface minimal.
VALID_TRANSPORTS: tuple[str, ...] = ("stdio", "http")

_DEFAULT_TRANSPORT = "stdio"
_DEFAULT_RANGE = "*"


@dataclass(frozen=True, slots=True)
class ExtensionSpec:
    """A validated, immutable declaration of one required MCP extension.

    ``version_range`` is a semver range string (``*`` means any); ``transport``
    is one of ``VALID_TRANSPORTS``. The record is hashable + thread-shareable so
    a connector pool can key on it without defensive copying."""

    name: str
    version_range: str
    transport: str


def discover_extensions(declared: list[dict]) -> tuple[ExtensionSpec, ...]:
    """Parse + validate a feature's declared extension list into ``ExtensionSpec``
    records, preserving declaration order. A missing/blank name or an unsupported
    transport is a hard ``McpExtensionLoadError`` (the feature must abort before
    any connection is attempted -- spec P2 acceptance #3 fails fast)."""
    specs: list[ExtensionSpec] = []
    for entry in declared:
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            raise McpExtensionLoadError(
                extension=str(name) if name else "<unnamed>",
                reason="declared extension is missing a non-empty 'name'",
            )
        name = name.strip()
        version_range = entry.get("version_range") or _DEFAULT_RANGE
        transport = entry.get("transport") or _DEFAULT_TRANSPORT
        if transport not in VALID_TRANSPORTS:
            raise McpExtensionLoadError(
                extension=name,
                reason=f"unsupported transport {transport!r}; expected one of {VALID_TRANSPORTS}",
            )
        specs.append(ExtensionSpec(name=name, version_range=str(version_range), transport=transport))
    return tuple(specs)


# --------------------------------------------------------------------------- #
# Minimal semver range matcher                                                  #
# --------------------------------------------------------------------------- #
_INF = (1 << 62, 0, 0)  # an upper sentinel larger than any real version triple


def version_satisfies(version_range: str, version: str) -> bool:
    """Return ``True`` if ``version`` satisfies ``version_range``.

    Supported forms (the subset a feature config uses):
      * ``*`` or empty -> any version
      * exact ``1.2.3``
      * caret ``^1.2.3`` -> compatible-with (locks the left-most non-zero part)
      * tilde ``~1.2.3`` -> patch-level (locks major.minor)
      * comparator list ``>=1.0.0,<2.0.0`` -> AND of ``>= > <= < == =`` clauses

    Pre-release / build metadata is ignored (truncated at the first ``-``/``+``)
    -- v0.1 features pin release versions, not pre-releases.
    """
    spec = version_range.strip()
    if spec in ("", "*"):
        return True
    actual = _parse(version)
    if spec[0] in "><=":
        return _satisfies_comparators(spec, actual)
    if spec.startswith("^"):
        lower = _parse(spec[1:])
        return lower <= actual < _caret_upper(lower)
    if spec.startswith("~"):
        lower, parts = _parse_counting(spec[1:])
        return lower <= actual < _tilde_upper(lower, parts)
    if "," in spec:
        return _satisfies_comparators(spec, actual)
    return actual == _parse(spec)


def _parse(version: str) -> tuple[int, int, int]:
    """Parse a dotted version into a 3-int triple, padding missing parts with 0
    and ignoring any pre-release/build suffix and trailing non-numeric junk."""
    return _parse_counting(version)[0]


def _parse_counting(version: str) -> tuple[tuple[int, int, int], int]:
    """Like ``_parse`` but also return how many numeric parts were present
    (1, 2, or 3) -- the tilde upper bound depends on that arity."""
    head = version.strip().split("-", 1)[0].split("+", 1)[0]
    nums: list[int] = []
    for piece in head.split("."):
        piece = piece.strip()
        if not piece.isdigit():
            break
        nums.append(int(piece))
        if len(nums) == 3:
            break
    count = len(nums)
    while len(nums) < 3:
        nums.append(0)
    return (nums[0], nums[1], nums[2]), count


def _caret_upper(lower: tuple[int, int, int]) -> tuple[int, int, int]:
    major, minor, patch = lower
    if major > 0:
        return (major + 1, 0, 0)
    if minor > 0:
        return (0, minor + 1, 0)
    return (0, 0, patch + 1)


def _tilde_upper(lower: tuple[int, int, int], parts: int) -> tuple[int, int, int]:
    major, minor, _ = lower
    if parts >= 2:
        return (major, minor + 1, 0)
    return (major + 1, 0, 0)


def _satisfies_comparators(spec: str, actual: tuple[int, int, int]) -> bool:
    for clause in spec.split(","):
        clause = clause.strip()
        if not clause:
            continue
        if not _one_comparator(clause, actual):
            return False
    return True


def _one_comparator(clause: str, actual: tuple[int, int, int]) -> bool:
    for op in (">=", "<=", "==", ">", "<", "="):
        if clause.startswith(op):
            bound = _parse(clause[len(op):])
            if op == ">=":
                return actual >= bound
            if op == "<=":
                return actual <= bound
            if op in ("==", "="):
                return actual == bound
            if op == ">":
                return actual > bound
            return actual < bound  # "<"
    # Bare version inside a comparator list means exact equality.
    return actual == _parse(clause)
