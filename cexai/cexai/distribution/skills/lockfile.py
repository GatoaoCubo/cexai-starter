"""skills.lock.v3 read/write + --frozen resolution (13 vercel-skills US P2).

Deterministic, byte-stable serialization of the frozen ``Lockfile`` / ``LockEntry``
(``cexai.distribution._shared.types``) so a checked-in lockfile round-trips
bit-for-bit (13 SC-001/002) and ``cexai skills install --frozen`` reproduces it with
no network. Serialization is CANONICAL: entries are emitted in a stable sorted order
regardless of in-memory order, so the same logical lockfile always produces the same
bytes (clean git diffs; reproducible CI). There is NO wall-clock field and NO
external YAML/TOML dependency (Article VIII -- stdlib only); the format is a small
hand-rolled sectioned text the parser reverses exactly.

``--frozen`` resolution (``resolve_frozen``) looks a ref up in the lockfile and:
  * returns the pinned entry when the upstream SHA matches (or no upstream SHA is
    supplied) -- the no-network reproducibility path (13 P2);
  * raises ``LockfileMismatchError`` (frozen ``_shared`` leaf) on a tree-SHA drift
    -- a HARD FAIL (13 SC-002);
  * raises ``FrozenLockViolationError`` (the lane-LOCAL leaf, sanctioned by the
    frozen ``_shared.errors`` docstring) when the ref is absent from the lockfile --
    ``--frozen`` rejects any source not present (13 P2 #1).

HONESTY NOTE (f7-honesty / R-230): ``load_lockfile`` used to be forward-tolerant to
a fault -- an unrecognized ``key = "value"`` line inside a ``[[skill]]`` block was
silently dropped, and a block missing a required field (``skill_ref`` / ``source`` /
``resolved_sha`` / ``artifact_sha256``) silently defaulted that field to ``""``. A
corrupted or hand-edited ``skills.lock.v3`` therefore parsed "successfully" into a
``Lockfile`` with holes nobody was told about. Both are now raised as
``LockfileParseError`` (the lane-LOCAL leaf below) -- surfaced, not swallowed.
``scope`` keeps its documented default (``"project"``) since it is the one field the
format has always treated as optional.

absorbs: 13_vercel-skills (+ 10_skills-sh artifact_sha256 identity field)
"""

from __future__ import annotations

from pathlib import Path

from cexai.distribution._shared.errors import DistributionError, LockfileMismatchError
from cexai.distribution._shared.types import LockEntry, Lockfile

__all__ = [
    "FrozenLockViolationError",
    "LockfileParseError",
    "dump_lockfile",
    "load_lockfile",
    "write_lockfile",
    "read_lockfile",
    "resolve_frozen",
]

_LOCKFILE_VERSION = "v3"
# The serialized LockEntry fields, in canonical emission order.
_ENTRY_FIELDS = ("skill_ref", "source", "resolved_sha", "artifact_sha256", "scope")
# Required to identify + pin a skill; only "scope" has a genuine optional default.
_REQUIRED_ENTRY_FIELDS = ("skill_ref", "source", "resolved_sha", "artifact_sha256")


# --------------------------------------------------------------------------- #
# Lane-LOCAL error leaves -- under the frozen DistributionError root.           #
# --------------------------------------------------------------------------- #
class FrozenLockViolationError(DistributionError):
    """A ``--frozen`` install referenced a skill not present in ``skills.lock.v3``
    (13 P2 #1) -- ``--frozen`` resolves ONLY against the lockfile and rejects any
    source it does not pin. Distinct from ``LockfileMismatchError`` (a SHA drift on a
    PRESENT entry): this is the ABSENT-entry reject path. ``skill_ref`` is the
    rejected ref. The lane-LOCAL leaf the frozen ``_shared.errors`` docstring
    sanctions for the ``--frozen`` not-in-lockfile case."""

    def __init__(self, skill_ref: str) -> None:
        self.skill_ref = skill_ref
        super().__init__(
            f"--frozen: {skill_ref!r} is not present in skills.lock.{_LOCKFILE_VERSION}"
        )


class LockfileParseError(DistributionError):
    """``skills.lock.v3`` text failed to parse cleanly (R-230). Distinct from
    ``LockfileMismatchError`` (a drifted-but-well-formed entry): this is a
    STRUCTURALLY corrupted lockfile -- either a ``[[skill]]`` block contains a key
    outside the canonical ``_ENTRY_FIELDS`` set (``unrecognized_key``), or a block
    closed without one of the required fields (``missing_field`` -- everything but
    ``scope``). ``entry_index`` is the 0-based ``[[skill]]`` block ordinal (the block
    is unreadable, so no ``skill_ref`` may exist to name it); the raw ``key`` is
    ``unrecognized_key``'s culprit, the raw field name is ``missing_field``'s. Never
    silently dropped / defaulted -- a hand-edited or corrupted lockfile must be
    surfaced, not parsed into a ``Lockfile`` with silent holes."""

    def __init__(
        self,
        entry_index: int,
        *,
        unrecognized_key: str | None = None,
        missing_field: str | None = None,
    ) -> None:
        self.entry_index = entry_index
        self.unrecognized_key = unrecognized_key
        self.missing_field = missing_field
        if unrecognized_key is not None:
            reason = f"unrecognized key {unrecognized_key!r}"
        else:
            reason = f"missing required field {missing_field!r}"
        super().__init__(
            f"skills.lock.{_LOCKFILE_VERSION} parse error in [[skill]] block "
            f"#{entry_index}: {reason}"
        )


def _quote(value: str) -> str:
    """Double-quote a scalar, escaping backslash + quote. ASCII-only output (the
    ascii-code rule)."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _unquote(token: str) -> str:
    """Reverse ``_quote`` for one ``key = "value"`` right-hand side."""
    token = token.strip()
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return token


def _entry_key(entry: LockEntry) -> tuple[str, str, str, str, str]:
    """Total-order sort key for canonical, deterministic entry emission."""
    return (
        entry.skill_ref,
        entry.scope,
        entry.source,
        entry.resolved_sha,
        entry.artifact_sha256,
    )


def dump_lockfile(lockfile: Lockfile) -> str:
    """Serialize a ``Lockfile`` to its canonical ``skills.lock.v3`` text. Entries are
    sorted by ``_entry_key`` so the bytes are deterministic regardless of in-memory
    order (13 SC-001); ends with a single trailing newline. ``dump(load(text)) ==
    text`` and ``dump(lf) == dump(lf-with-reordered-entries)``."""
    lines: list[str] = [f"version = {_quote(lockfile.version)}", ""]
    for entry in sorted(lockfile.entries, key=_entry_key):
        lines.append("[[skill]]")
        for field in _ENTRY_FIELDS:
            lines.append(f"{field} = {_quote(getattr(entry, field))}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def _finish_entry(fields: dict[str, str], entry_index: int) -> LockEntry:
    """Build a ``LockEntry`` from a parsed field map (``scope`` defaults to
    ``"project"`` -- the one genuinely optional field). Raises ``LockfileParseError``
    if any of the four REQUIRED fields (``skill_ref`` / ``source`` / ``resolved_sha``
    / ``artifact_sha256``) is absent -- a corrupted/truncated block must be surfaced,
    never silently frozen into an entry with a blank identity (R-230)."""
    for field in _REQUIRED_ENTRY_FIELDS:
        if field not in fields:
            raise LockfileParseError(entry_index, missing_field=field)
    return LockEntry(
        skill_ref=fields["skill_ref"],
        source=fields["source"],
        resolved_sha=fields["resolved_sha"],
        artifact_sha256=fields["artifact_sha256"],
        scope=fields.get("scope", "project"),
    )


def load_lockfile(text: str) -> Lockfile:
    """Parse canonical ``skills.lock.v3`` text into a ``Lockfile``. Entries are
    returned in canonical sorted order so a parsed lockfile re-serializes
    byte-identically (13 SC-001/002).

    Blank lines are skipped and a line with no ``=`` is ignored (whitespace / stray
    text tolerance). Within a ``[[skill]]`` block, a ``key = "value"`` line whose
    ``key`` is outside the canonical ``_ENTRY_FIELDS`` set raises
    ``LockfileParseError`` (R-230 -- an unrecognized key used to be silently
    dropped); a block that closes (at the next ``[[skill]]`` or end of text) without
    one of the four required fields also raises ``LockfileParseError`` (previously
    silently defaulted to ``""``). Before the first ``[[skill]]``, only ``version``
    is recognized; any other top-level ``key = value`` line is ignored (the header
    has no other canonical fields today)."""
    version = _LOCKFILE_VERSION
    entries: list[LockEntry] = []
    current: dict[str, str] | None = None
    entry_index = -1

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line == "[[skill]]":
            if current is not None:
                entries.append(_finish_entry(current, entry_index))
            current = {}
            entry_index += 1
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = _unquote(value)
        if current is None:
            if key == "version":
                version = value
            continue
        if key not in _ENTRY_FIELDS:
            raise LockfileParseError(entry_index, unrecognized_key=key)
        current[key] = value

    if current is not None:
        entries.append(_finish_entry(current, entry_index))

    return Lockfile(version=version, entries=tuple(sorted(entries, key=_entry_key)))


def write_lockfile(path: str | Path, lockfile: Lockfile) -> Path:
    """Write ``lockfile`` to ``path`` as canonical bytes (creating parents). Returns
    the written ``Path``."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_lockfile(lockfile), encoding="utf-8")
    return target


def read_lockfile(path: str | Path) -> Lockfile:
    """Read + parse a ``skills.lock.v3`` file into a ``Lockfile``."""
    return load_lockfile(Path(path).read_text(encoding="utf-8"))


def resolve_frozen(
    lockfile: Lockfile,
    skill_ref: str,
    upstream_sha: str | None = None,
    *,
    scope: str | None = None,
) -> LockEntry:
    """Resolve ``skill_ref`` against ``lockfile`` under ``--frozen`` (13 P2). Returns
    the pinned ``LockEntry`` (no network). Raises ``FrozenLockViolationError`` if the
    ref is absent (13 P2 #1); raises ``LockfileMismatchError`` if ``upstream_sha`` is
    supplied and drifts from the pinned ``resolved_sha`` -- a HARD FAIL (13 SC-002).
    ``scope`` optionally narrows the match (13 E2: same name in two scopes)."""
    match: LockEntry | None = None
    for entry in lockfile.entries:
        if entry.skill_ref == skill_ref and (scope is None or entry.scope == scope):
            match = entry
            break

    if match is None:
        raise FrozenLockViolationError(skill_ref)
    if upstream_sha is not None and upstream_sha != match.resolved_sha:
        raise LockfileMismatchError(skill_ref, match.resolved_sha, upstream_sha)
    return match
