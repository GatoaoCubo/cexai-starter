"""Open-variable discovery -- build a read-only index over artifact frontmatters
and query it (ADR 022 D-022-03).

Discovery answers "given a kind / a var name / a type, which open variables are
already in use?" It NEVER creates, freezes, or mutates -- it informs the
compiler's Layer-1 context assembly and the GDP gate's top-3 candidate
suggestions. ``build_index`` aggregates each var name across all artifacts that
declare it into a single entry (the D-022-03 schema). The four query functions
(``lookup`` / ``for_kind`` / ``for_type`` / ``search``) NEVER raise on missing
data: a miss is ``None`` (lookup) or ``[]`` (the collection queries).

``build_index`` is pure and deterministic -- ``last_seen`` is derived from a
timestamp already present in the artifact data (``last_seen`` / ``_frozen_at`` /
``date`` / ``updated_at``), never from the wall clock -- so the same corpus
always yields the same index (testable, diff-stable for the post-commit rebuild).

Spec provenance: cexai-specs/_decisions/adr_022_open_variables_full_protocol.md
(D-022-03 discovery index + query API).

absorbs: cexai-specs/open-variables-protocol
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from typing import Any

__all__ = [
    "build_index",
    "lookup",
    "for_kind",
    "for_type",
    "search",
    "set_index",
]

# Artifact timestamp fields consulted for ``last_seen``, in priority order.
_TIMESTAMP_FIELDS: tuple[str, ...] = ("last_seen", "_frozen_at", "date", "updated_at")

# The process default index -- consulted when a query is called without an
# explicit ``index``. Populated via ``set_index`` (e.g. after a post-commit
# rebuild). Empty until set, so the no-arg query form never raises.
_INDEX: list[dict[str, Any]] = []


# --------------------------------------------------------------------------- #
# build                                                                         #
# --------------------------------------------------------------------------- #
def build_index(artifacts: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate the ``open_vars`` declared across ``artifacts`` into a list of
    D-022-03 index entries, one per distinct var name, sorted by ``var_name``.

    Tolerant by contract (never raises on malformed data): a non-mapping
    artifact, an artifact with no ``open_vars`` or a non-list ``open_vars``, and
    a declaration without a ``name`` are all skipped. ``type_token`` is the most
    frequently observed type for the var; ``last_seen`` is the max artifact
    timestamp (ISO strings compare lexically) or ``None`` if none was recorded.
    """
    accum: dict[str, _Accumulator] = {}
    for artifact in artifacts:
        frontmatter = _frontmatter_of(artifact)
        if frontmatter is None:
            continue
        declarations = frontmatter.get("open_vars")
        if not isinstance(declarations, list):
            continue
        kind = frontmatter.get("kind")
        timestamp = _timestamp_of(frontmatter)
        for declaration in declarations:
            if not isinstance(declaration, Mapping):
                continue
            name = declaration.get("name")
            if not name:
                continue
            accum.setdefault(name, _Accumulator()).observe(declaration, kind, timestamp)
    return [accum[name].to_entry(name) for name in sorted(accum)]


class _Accumulator:
    """Mutable per-var fold; emits an immutable D-022-03 entry via ``to_entry``."""

    __slots__ = ("types", "kinds", "roles", "stages", "hints", "count", "timestamps")

    def __init__(self) -> None:
        self.types: Counter[str] = Counter()
        self.kinds: set[str] = set()
        self.roles: set[str] = set()
        self.stages: set[str] = set()
        self.hints: set[str] = set()
        self.count: int = 0
        self.timestamps: list[str] = []

    def observe(self, declaration: Mapping[str, Any], kind: Any, timestamp: str | None) -> None:
        self.count += 1
        type_token = declaration.get("type")
        if isinstance(type_token, str):
            self.types[type_token] += 1
        if isinstance(kind, str):
            self.kinds.add(kind)
        role = declaration.get("filler_role")
        if isinstance(role, str):
            self.roles.add(role)
        stage = declaration.get("filler_stage")
        if isinstance(stage, str):
            self.stages.add(stage)
        hints = declaration.get("context_hints")
        if isinstance(hints, list):
            self.hints.update(h for h in hints if isinstance(h, str))
        if timestamp is not None:
            self.timestamps.append(timestamp)

    def to_entry(self, name: str) -> dict[str, Any]:
        most_common = self.types.most_common(1)
        return {
            "var_name": name,
            "type_token": most_common[0][0] if most_common else None,
            "kinds_using": sorted(self.kinds),
            "filler_roles_observed": sorted(self.roles),
            "filler_stages_observed": sorted(self.stages),
            "context_hints_observed": sorted(self.hints),
            "occurrence_count": self.count,
            "last_seen": max(self.timestamps) if self.timestamps else None,
        }


def _frontmatter_of(artifact: Any) -> Mapping[str, Any] | None:
    if not isinstance(artifact, Mapping):
        return None
    nested = artifact.get("frontmatter")
    if isinstance(nested, Mapping):
        return nested
    return artifact


def _timestamp_of(frontmatter: Mapping[str, Any]) -> str | None:
    for field in _TIMESTAMP_FIELDS:
        value = frontmatter.get(field)
        if isinstance(value, str) and value:
            return value
    return None


# --------------------------------------------------------------------------- #
# query API -- never raise on a miss                                            #
# --------------------------------------------------------------------------- #
def set_index(entries: Iterable[Mapping[str, Any]]) -> None:
    """Replace the process default index (e.g. after a post-commit rebuild). The
    no-``index`` query form then reads from it."""
    global _INDEX
    _INDEX = [dict(entry) for entry in entries]


def lookup(name: str, index: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    """Return the entry whose ``var_name`` equals ``name``, or ``None`` on a
    miss (exact match; the singular query)."""
    for entry in _resolve(index):
        if entry.get("var_name") == name:
            return entry
    return None


def for_kind(kind: str, index: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return every entry observed in ``kind`` (``[]`` on a miss)."""
    return [entry for entry in _resolve(index) if kind in entry.get("kinds_using", ())]


def for_type(type_token: str, index: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return every entry whose ``type_token`` equals ``type_token`` (``[]`` on a
    miss)."""
    return [entry for entry in _resolve(index) if entry.get("type_token") == type_token]


def search(query: str, index: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Case-insensitive substring search over a var's name, type, kinds, and
    observed context hints (``[]`` on a miss). v1 is substring-only -- embedding
    search is deferred (D-022-03 out-of-scope)."""
    needle = query.lower()
    matches: list[dict[str, Any]] = []
    for entry in _resolve(index):
        if needle in _haystack(entry):
            matches.append(entry)
    return matches


def _resolve(index: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return _INDEX if index is None else index


def _haystack(entry: Mapping[str, Any]) -> str:
    parts: list[str] = [str(entry.get("var_name", "")), str(entry.get("type_token", ""))]
    parts.extend(str(k) for k in entry.get("kinds_using", ()))
    parts.extend(str(h) for h in entry.get("context_hints_observed", ()))
    return " ".join(parts).lower()
