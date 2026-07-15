"""CrossAgentInstaller -- resolve a skill across sources into a typed InstallPlan.

The concrete implementation of the frozen ``SkillInstaller`` Protocol
(``cexai.distribution._shared.types.SkillInstaller``) for 10_skills-sh + 13
vercel-skills. ``install(skill_ref, sources)`` resolves the ref through the ordered
sources -- a configured ``custom_registry`` is consulted BEFORE the public
``registry`` (10 P2 #2) -- pins the resolved GitHub tree SHA (``skillFolderHash``,
13 FR-002), computes the per-detected-agent target directories (13 P1 #2,
``@vercel/detect-agent``), links (default) or copies (``--copy``, 13 FR-005) the
skill into each, and returns a typed ``InstallPlan``. Re-running an install on an
unchanged ``(skill_ref, resolved_sha, scope)`` is idempotent -- it rewrites nothing
(13 P1 #4). Every install emits a ``reasoning_trace`` entry (13 FR-012; the F7
GOVERN wiring is a later wave -- here we EMIT and expose the trace).

Offline-first (Article XIV / Article VIII -- import-light, stdlib only): the three
seams are INJECTED callables so the whole path is offline-testable with fakes --
``resolver`` (``(source, skill_ref) -> ResolvedSource | None``; the git / registry /
local backend, with ``@vercel/detect-agent`` and GitPython landing as lazy heavy
deps in a later wave), ``detector`` (``scope -> target_dirs``; the agent-detection
seam), and ``linker`` (``(skill_ref, target_dir, strategy) -> None``; the
symlink/copy seam). The unconfigured defaults are deterministic and offline: the
default resolver derives both SHAs purely from the (normalized) skill_ref -- so the
``artifact_sha256`` is the SAME across all four sources for one logical skill (the
10 SC-001 cross-source identity key) -- and the default detector links into no
directories (a no-arg ``CrossAgentInstaller()`` writes nothing). Production injects
the live backends; offline correctness does not depend on them.

``SkillSourceUnavailableError`` is the lane-LOCAL leaf for 13 E1 (a deleted /
unreachable upstream, or no source resolving the ref) -- it subclasses the frozen
``DistributionError`` per the sanctioned extension pattern (see
``cexai.distribution._shared.errors`` module docstring). On this error the caller's
lockfile is left untouched (13 E1).

absorbs: 10_skills-sh + 13_vercel-skills
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from cexai.distribution._shared.errors import DistributionError
from cexai.distribution._shared.types import InstallPlan, LockEntry

__all__ = [
    "ResolvedSource",
    "SourceResolver",
    "AgentDetector",
    "SkillLinker",
    "SkillSourceUnavailableError",
    "CrossAgentInstaller",
    "build_installer",
]


# --------------------------------------------------------------------------- #
# Lane-LOCAL error leaf (13 E1) -- under the frozen DistributionError root.     #
# --------------------------------------------------------------------------- #
class SkillSourceUnavailableError(DistributionError):
    """A skill source is unavailable (13 E1) -- the upstream GitHub/GitLab repo was
    deleted / is unreachable, or no configured source resolved the ref. The install
    aborts and the lockfile is NOT modified. ``skill_ref`` is the affected skill and
    ``reason`` is the human-readable cause, surfaced for the reasoning_trace. This is
    the lane-LOCAL leaf the frozen ``_shared.errors`` docstring sanctions for 13 E1
    (it is not in the frozen set; it subclasses ``DistributionError``)."""

    def __init__(self, skill_ref: str, reason: str) -> None:
        self.skill_ref = skill_ref
        self.reason = reason
        super().__init__(f"skill source unavailable for {skill_ref!r}: {reason}")


# --------------------------------------------------------------------------- #
# The resolved-source seam vocabulary + the three injected backend types.       #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class ResolvedSource:
    """One source's resolution of a skill_ref. ``source`` is the ``InstallSource``
    that resolved (kept ``str`` for headroom, matching ``InstallPlan.source``);
    ``resolved_sha`` is the pinned GitHub tree SHA (``skillFolderHash``, the 13
    FR-002 reproducibility key); ``artifact_sha256`` is the SHA256 of the installed
    artifact (the 10 SC-001 cross-source identity key -- equal across all four
    sources for one logical skill)."""

    source: str
    resolved_sha: str
    artifact_sha256: str


# ``(source, skill_ref) -> ResolvedSource | None``: ``None`` means this source does
# not have the ref (fall through to the next); raising ``SkillSourceUnavailableError``
# means the source is selected but the upstream is gone (13 E1).
SourceResolver = Callable[[str, str], "ResolvedSource | None"]
# ``scope -> target_dirs``: the per-detected-agent install directories (the
# ``@vercel/detect-agent`` seam, 13 FR-003).
AgentDetector = Callable[[str], tuple[str, ...]]
# ``(skill_ref, target_dir, strategy) -> None``: the symlink/copy seam (13 FR-005).
SkillLinker = Callable[[str, str, str], None]


def _normalize_ref(skill_ref: str) -> str:
    """Canonicalize a skill_ref for content-identity hashing. Kept deliberately
    light (strip surrounding whitespace) so the same ref always hashes identically
    across sources -- the cross-source identity contract (10 SC-001)."""
    return skill_ref.strip()


def _default_resolver(source: str, skill_ref: str) -> ResolvedSource:
    """The unconfigured, offline, deterministic resolver. Derives BOTH SHAs purely
    from the normalized skill_ref (NOT the source), so a no-arg installer produces a
    valid plan with no network AND the ``artifact_sha256`` is identical across all
    four sources for one logical skill (10 SC-001). Production injects the live
    git / registry / local backend; offline correctness does not depend on it. (The
    SHAs are content-identity digests, not security tokens.)"""
    ref = _normalize_ref(skill_ref).encode("utf-8")
    return ResolvedSource(
        source=source,
        resolved_sha=hashlib.sha1(ref).hexdigest(),  # noqa: S324 - identity, not crypto
        artifact_sha256=hashlib.sha256(ref).hexdigest(),
    )


def _default_detector(scope: str) -> tuple[str, ...]:
    """The unconfigured detector: detect no agents (offline-safe). A no-arg
    ``CrossAgentInstaller()`` therefore links into nothing -- ``install`` plans and
    writes no files. Production injects the ``@vercel/detect-agent`` backend."""
    return ()


def _default_linker(skill_ref: str, target_dir: str, strategy: str) -> None:
    """The unconfigured linker: a no-op (offline-safe). With the default detector
    producing no target dirs it is never called; an injected detector + this linker
    plans target dirs without touching the filesystem."""
    return None


def _ordered_sources(sources: tuple[str, ...]) -> tuple[str, ...]:
    """Order the requested sources so a configured ``custom_registry`` is consulted
    FIRST (10 P2 #2), preserving the caller's relative order otherwise."""
    custom = tuple(s for s in sources if s == "custom_registry")
    rest = tuple(s for s in sources if s != "custom_registry")
    return custom + rest


class CrossAgentInstaller:
    """Concrete ``SkillInstaller``: cross-agent skill install (10 + 13).

    Construct with optional injected seams -- ``resolver`` (the git / registry /
    local backend), ``detector`` (the ``@vercel/detect-agent`` seam), and ``linker``
    (the symlink/copy seam) -- plus the resolved ``scope`` (``project`` default, or
    ``global`` for ``-g``, 13 FR-004) and ``link_strategy`` (``symlink`` default, or
    ``copy`` for ``--copy``, 13 FR-005). All optional: a no-arg instance is
    constructible and resolves deterministically offline (the contract-test path)."""

    def __init__(
        self,
        *,
        resolver: SourceResolver | None = None,
        detector: AgentDetector | None = None,
        linker: SkillLinker | None = None,
        scope: str = "project",
        link_strategy: str = "symlink",
    ) -> None:
        self._resolver: SourceResolver = resolver if resolver is not None else _default_resolver
        self._detector: AgentDetector = detector if detector is not None else _default_detector
        self._linker: SkillLinker = linker if linker is not None else _default_linker
        self._scope = scope
        self._link_strategy = link_strategy
        # Idempotency ledger: applied ``(skill_ref, resolved_sha, scope)`` keys.
        self._applied: set[tuple[str, str, str]] = set()
        self._traces: list[str] = []

    @property
    def reasoning_trace(self) -> tuple[str, ...]:
        """The accumulated reasoning_trace entries (13 FR-012). One entry per
        ``install`` call; the F7 GOVERN gate that consumes it is wired in a later
        wave -- here the trace is EMITted and exposed."""
        return tuple(self._traces)

    # -- SkillInstaller protocol -------------------------------------------- #
    def install(self, skill_ref: str, sources: tuple[str, ...]) -> InstallPlan:
        """Resolve ``skill_ref`` across ``sources`` (custom_registry first) into a
        typed ``InstallPlan``, link/copy it into the detected agent dirs, and emit a
        reasoning_trace entry. Idempotent on an unchanged ``(skill_ref,
        resolved_sha, scope)`` (13 P1 #4). Raises ``SkillSourceUnavailableError`` if
        no source resolves the ref / the upstream is gone (13 E1, lockfile
        untouched)."""
        resolved = self._resolve(skill_ref, sources)
        target_dirs = tuple(self._detector(self._scope))

        key = (skill_ref, resolved.resolved_sha, self._scope)
        applied = key not in self._applied
        if applied:
            for target_dir in target_dirs:
                self._linker(skill_ref, target_dir, self._link_strategy)
            self._applied.add(key)

        self._traces.append(
            f"install {skill_ref!r}: source={resolved.source} "
            f"sha={resolved.resolved_sha} scope={self._scope} "
            f"dirs={len(target_dirs)} strategy={self._link_strategy} applied={applied}"
        )
        return InstallPlan(
            skill_ref=skill_ref,
            source=resolved.source,
            resolved_sha=resolved.resolved_sha,
            scope=self._scope,
            target_dirs=target_dirs,
            link_strategy=self._link_strategy,
        )

    # -- lockfile atom (13 P1: "writes a lockfile entry") -------------------- #
    def lock_entry(self, skill_ref: str, sources: tuple[str, ...]) -> LockEntry:
        """Resolve ``skill_ref`` and project the ``skills.lock.v3`` ``LockEntry`` --
        carrying both the pinned ``resolved_sha`` (13 FR-002) and the
        ``artifact_sha256`` cross-source identity key (10 SC-001). The lockfile
        read/write + ``--frozen`` resolution live in the sibling ``lockfile``
        module; this is the resolution atom they record."""
        resolved = self._resolve(skill_ref, sources)
        return LockEntry(
            skill_ref=skill_ref,
            source=resolved.source,
            resolved_sha=resolved.resolved_sha,
            artifact_sha256=resolved.artifact_sha256,
            scope=self._scope,
        )

    # -- internals ----------------------------------------------------------- #
    def _resolve(self, skill_ref: str, sources: tuple[str, ...]) -> ResolvedSource:
        """Try the ordered sources (custom_registry first); the first that resolves
        (non-``None``) wins. A resolver may raise ``SkillSourceUnavailableError`` for
        a selected-but-gone upstream (13 E1) -- it propagates. If no source resolves,
        raise ``SkillSourceUnavailableError`` (the ref is unavailable everywhere)."""
        for source in _ordered_sources(sources):
            resolved = self._resolver(source, skill_ref)
            if resolved is not None:
                return resolved
        raise SkillSourceUnavailableError(
            skill_ref, f"no configured source resolved it (tried {list(sources)})"
        )


def build_installer(
    *,
    resolver: SourceResolver | None = None,
    detector: AgentDetector | None = None,
    linker: SkillLinker | None = None,
    scope: str = "project",
    link_strategy: str = "symlink",
) -> CrossAgentInstaller:
    """Convenience constructor mirroring the tools subsystem's ``build_fetcher``.
    Returns a ready ``CrossAgentInstaller`` with the given (optional) seams."""
    return CrossAgentInstaller(
        resolver=resolver,
        detector=detector,
        linker=linker,
        scope=scope,
        link_strategy=link_strategy,
    )
