"""Frozen type contracts for the CEXAI distribution layer -- the v0.5-W0 freeze.

These names and shapes are FROZEN for the whole v0.5 (distribution + methodology)
milestone. Every v0.5 impl cell -- skill packaging/install, cross-agent install
CLI, cross-runtime verify, SPARC methodology -- imports these symbols and MUST NOT
change their names or fields. If a shape must evolve, that is a versioned,
peer-reviewed change, not an in-flight edit. This mirrors the v0.1 foundation,
v0.2 memory, v0.3-W0 orchestration, v0.3-W3a governance, and v0.4-W0 tools freeze
discipline in ``cexai.{foundation,memory,orchestration,governance,tools}.
_shared.types``.

Design constraints (Article VIII -- Anti-Abstraction):
  * stdlib typing only -- NO pydantic, NO npm shellout, NO ``@vercel/detect-agent``
    / requests / GitPython in this contract. The heavy deps land in the impl waves
    when actually wired; the freeze stays import-light (its one cross-package
    import is the already-frozen v0.3 orchestration ``SparcPhaseId``, reused not
    redefined).
  * every value type is an immutable ``@dataclass(frozen=True, slots=True)``.
  * collection fields are tuples / read-only mappings so instances are safely
    shareable across threads, nuclei, and providers without defensive copying.

Two distribution subsystems share one vocabulary here:
  * skills (10 skills-sh + 13 vercel-skills) -- InstallSource, InstallScope,
        SkillManifest, InstallPlan, LockEntry, Lockfile, SkillRegistry,
        CrossRuntimeReport; SkillInstaller, SkillVerifier.
  * sparc  (04 claude-flow)                  -- SparcPhase, SparcTemplate;
        SparcMethodology.

These compose with -- they do NOT replace -- the existing substrate. The SPARC
projection REUSES the v0.3 orchestration ``SparcPhaseId`` (imported below, never
redefined) and the existing ``pipeline_template`` kind; the skills installer emits
a ``reasoning_trace`` (13 FR-012) and validates installed frontmatter against
``.cex/kinds_meta.json`` (13 FR-013) through the existing substrate. This module
does NOT duplicate that vocabulary; it references it.

TAXONOMY NOTE (founder rule, taxonomy-neutral wave): these are Python CODE types.
Per N07's locked v0.5 decision this wave -- and the whole v0.5 milestone --
registers ZERO kinds and does NOT touch ``.cex/kinds_meta.json`` (the full
disposition lives in ``cexai/docs/adr_v05_distribution_taxonomy.md``).
  * ``sparc_phase`` (the 04 spec / FR-005 CALLS it a "new top-level kind") is
    REJECTED as a kind: the five SPARC phases are a PIPELINE (a scenario-indexed
    agent sequence WITH a revision loop -- the ``refinement`` phase) -> REUSE the
    existing ``pipeline_template`` kind. The founder rule OVERRIDES the spec
    author's "new kind" claim; it is not registered. ``SparcPhase`` here is a
    runtime PROJECTION over ``SparcPhaseId`` + ``pipeline_template``, NOT a kind
    (precedent: FetchResult, Span, TopologyRun, AuthToken).
  * ``skill`` (10) REUSES the existing ``skill`` kind (agentskills.io frontmatter
    compliance is VALIDATED at publish, not a schema mutation). ``skill_registry``
    (10) REUSES ``marketplace_app_manifest`` (``marketplace_type: skills``, a
    value). ``MethodologyChoice`` (04) REUSES ``decision_record``
    (``decision_type: methodology_choice``, a value). ``reasoning_trace`` (13
    F7 gate) REUSES the existing ``reasoning_trace`` kind (its F7 GOVERN
    integration is wired by a later impl wave, not this freeze). All five reuse
    targets are confirmed present in the registry.
  * Lockfile / LockEntry / InstallPlan / SkillManifest / SkillRegistry /
    CrossRuntimeReport / SparcPhase / SparcTemplate are RUNTIME DATACLASSES, not
    kinds -- transient runtime data with no persisted-artifact form.

Spec provenance:
  * cexai-specs/10_skills-sh/spec.md -- US P1/P2/P3 + FR-001..007 + SC-001/002/003
        + Key Entities (Skill, skill_registry) -- skills packaging/install/verify.
  * cexai-specs/13_vercel-skills/spec.md -- US P1/P2/P3 + FR-001..015 + SC-001..006
        + E1/E2 + Key Entities (lockfile) -- cross-agent install CLI.
  * cexai-specs/04_claude-flow/spec.md -- US P1 + FR-001..006 + SC-001/002 + Key
        Entities (SparcPhase, MethodologyChoice) -- SPARC methodology.

absorbs: 10_skills-sh + 13_vercel-skills + 04_claude-flow
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, Protocol, runtime_checkable

# The five SPARC phase ids are ALREADY frozen in the v0.3 orchestration contract.
# Reuse them; do NOT redefine them here (founder rule -- one canonical vocabulary).
from cexai.orchestration._shared.types import SparcPhaseId

__all__ = [
    # skills (10_skills-sh + 13_vercel-skills)
    "InstallSource",
    "InstallScope",
    "SkillManifest",
    "InstallPlan",
    "LockEntry",
    "Lockfile",
    "SkillRegistry",
    "CrossRuntimeReport",
    # sparc (04_claude-flow)
    "SparcPhase",
    "SparcTemplate",
    # protocols (the seams the impl waves implement)
    "SkillInstaller",
    "SkillVerifier",
    "SparcMethodology",
]

# Immutable empty mapping -- safe shared default for the optional ``frontmatter`` /
# ``skills`` fields. A frozen dataclass cannot take a dict default (mutable);
# MappingProxyType is read-only, so one shared instance is correct.
_EMPTY_CONFIG: Mapping[str, Any] = MappingProxyType({})


# --------------------------------------------------------------------------- #
# Skills subsystem (cexai-specs/10_skills-sh + 13_vercel-skills) --             #
#   agentskills.io packaging + cross-agent install + cross-runtime verify.      #
# --------------------------------------------------------------------------- #
# The install source classes (10 FR-002 / 13 FR-001). The SAME logical skill
# installs IDENTICALLY (SHA256 match, 10 SC-001) from all four: ``registry`` is the
# public skills.sh marketplace (a ``user/repo`` alias resolves here);
# ``custom_registry`` is a configured private registry, consulted FIRST (10 P2 #2);
# ``git`` is a ``git+https`` / GitHub / GitLab URL (13 FR-001 -- the GitHub-vs-GitLab
# host is a runtime detail, both are one git source); ``local`` is a local path
# (symlinked for dev, 13 FR-005). Kept ``str`` on ``InstallPlan.source`` for
# headroom; this Literal is the canonical four.
InstallSource = Literal[
    "registry",
    "custom_registry",
    "git",
    "local",
]

# The install scope (13 US P3 / FR-004). ``project`` (default, no flag) installs
# into the current project's per-agent dirs; ``global`` (the ``-g`` flag) installs
# into the user's global agent dir (e.g. ``~/.claude/skills/``). ``skills list``
# separates the two (13 P3 #3). Kept ``str`` on the wire for headroom.
InstallScope = Literal[
    "project",
    "global",
]


@dataclass(frozen=True, slots=True)
class SkillManifest:
    """The agentskills.io-compliant manifest of a packaged skill (10 US P1 / Key
    Entities: Skill; 13 FR-006 SKILL.md). RUNTIME DATA, not a kind -- the persisted
    artifact REUSES the existing ``skill`` kind (see module TAXONOMY NOTE); this is
    its in-memory shape. ``name`` / ``version`` identify it; ``frontmatter`` is the
    read-only SKILL.md / agentskills.io frontmatter map (it carries the ``kind``
    validated against ``.cex/kinds_meta.json`` per 13 FR-013, and the ``open_vars``
    required when the body declares ``{{...}}`` per 13 FR-014); ``assets`` is the
    ordered tuple of bundled asset paths (an asset >= 10MB is externalized per 10
    FR-007 -- an impl-layer concern); ``runtime_compatibility`` is the ordered tuple
    of runtime ids the skill CLAIMS to support (e.g. ``("claude-code", "ollama")``)
    -- an empty tuple is no cross-runtime claim, so cross-runtime verification is
    skipped (10 P3 / SC-003, the V10-F2 "claiming must pass" bar)."""

    name: str
    version: str
    frontmatter: Mapping[str, Any] = _EMPTY_CONFIG
    assets: tuple[str, ...] = ()
    runtime_compatibility: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class InstallPlan:
    """The resolved, pre-execution plan for one skill install (13 US P1 /
    FR-001/003/005). Produced by ``SkillInstaller.install`` BEFORE any filesystem
    write, so the plan is inspectable and the install is reproducible. ``skill_ref``
    is the requested source string (e.g. ``@vendor/release-notes``); ``source`` is
    the resolved ``InstallSource`` (kept ``str`` for headroom); ``resolved_sha`` is
    the pinned GitHub tree SHA (the ``skillFolderHash``, 13 FR-002 -- the
    determinism key); ``scope`` is the resolved ``InstallScope`` (kept ``str``);
    ``target_dirs`` is the ordered tuple of per-detected-agent directories the skill
    links/copies into (13 P1 #2, ``@vercel/detect-agent`` 55+ agents);
    ``link_strategy`` is ``symlink`` (default, 13 FR-005) or ``copy`` (``--copy``,
    systems without symlink support). Re-running an install on an unchanged source
    is idempotent (13 P1 #4): a plan with the same ``(skill_ref, resolved_sha,
    scope)`` rewrites nothing."""

    skill_ref: str
    source: str
    resolved_sha: str
    scope: str = "project"
    target_dirs: tuple[str, ...] = ()
    link_strategy: str = "symlink"


@dataclass(frozen=True, slots=True)
class LockEntry:
    """One ``skills.lock.v3`` entry (13 FR-002 / US P2). The reproducibility atom:
    ``skill_ref`` is the source string; ``source`` is the ``InstallSource`` it
    resolved through; ``resolved_sha`` is the pinned GitHub tree SHA
    (``skillFolderHash``) -- a drift between this and the upstream tree SHA is the
    ``--frozen`` HARD FAIL (13 SC-002, raises ``LockfileMismatchError``);
    ``artifact_sha256`` is the SHA256 of the INSTALLED skill artifact -- the
    cross-source identity key that MUST match across all four sources for the same
    logical skill (10 SC-001); ``scope`` is the ``InstallScope`` it installed into.
    Every field is read-only so the entry serializes deterministically and
    round-trips byte-stably (13 SC-001/002)."""

    skill_ref: str
    source: str
    resolved_sha: str
    artifact_sha256: str
    scope: str = "project"


@dataclass(frozen=True, slots=True)
class Lockfile:
    """A ``skills.lock.v3`` lockfile (13 FR-002 / US P2). ``version`` is the lockfile
    format version (``v3``; an older version is wiped and reinstalled per 13 P2 #3);
    ``entries`` is the ordered tuple of ``LockEntry`` -- ordered so the file
    serializes deterministically and round-trips byte-stably (the ``--frozen``
    reproducibility contract, 13 SC-001/002). The lockfile is checked into git and
    CI verifies its presence (13 P2 #4); ``cexai skills install --frozen`` resolves
    every skill to its exact ``resolved_sha`` with no ``latest`` network
    resolution."""

    version: str
    entries: tuple[LockEntry, ...] = ()


@dataclass(frozen=True, slots=True)
class SkillRegistry:
    """The runtime projection of a skills marketplace registry (10 US P2 / Key
    Entities: skill_registry). RUNTIME DATA, not a kind -- it REUSES the existing
    ``marketplace_app_manifest`` kind with ``marketplace_type: skills`` (a value,
    not a schema mutation; see module TAXONOMY NOTE). ``registry_id`` is the handle
    (e.g. ``skills.sh``); ``url`` is its endpoint; ``marketplace_type`` is the
    discriminator (defaults ``skills``); ``skills`` is the ordered tuple of skill
    refs the registry indexes. A configured ``custom_registry`` is consulted before
    the public ``registry`` (10 P2 #2)."""

    registry_id: str
    url: str
    marketplace_type: str = "skills"
    skills: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CrossRuntimeReport:
    """The result of a cross-runtime parity check (10 US P3 / SC-003; 13 SC-004).
    ``skill_name`` is the verified skill; ``runtimes`` is the ordered tuple of
    runtime ids exercised (e.g. ``("claude-code", "ollama")`` minimum, 10 P3, or
    ``("codex", "gemini")`` for the 13 SC-004 SKILL.md portability check);
    ``parity`` is ``True`` when the skill behaves identically across every claimed
    runtime; ``failures`` is the ordered tuple of runtime ids that DIVERGED (the
    ``[CROSS_RUNTIME_FAIL]`` set, 10 P3 #2) -- non-empty exactly when
    ``parity is False``. A failure here does NOT auto-demote the skill (V10-F3):
    ``SkillVerifier.verify`` RETURNS this report and the maintainer is asked to
    review; the publish gate is what RAISES ``CrossRuntimeParityError`` for a skill
    that CLAIMS cross-runtime yet fails."""

    skill_name: str
    runtimes: tuple[str, ...]
    parity: bool
    failures: tuple[str, ...] = ()


# --------------------------------------------------------------------------- #
# SPARC subsystem (cexai-specs/04_claude-flow) -- opt-in methodology pipeline.   #
# --------------------------------------------------------------------------- #
# The five ordered phase ids (``SparcPhaseId``: specification / pseudocode /
# architecture / refinement / code) are ALREADY frozen in the v0.3 orchestration
# contract and are IMPORTED above, never redefined here. The founder rule REUSES the
# existing ``pipeline_template`` kind for the 5-phase pipeline (a scenario-indexed
# agent sequence WITH a revision loop -- the ``refinement`` phase -- which is exactly
# the pipeline_template boundary); ``sparc_phase`` is NOT registered as a kind (04
# FR-005 overridden, see the v0.5 taxonomy ADR). The two dataclasses below are
# runtime PROJECTIONS over that reused vocabulary.
@dataclass(frozen=True, slots=True)
class SparcPhase:
    """The runtime PROJECTION of one SPARC phase for a feature (04 US P1 / Key
    Entities: SparcPhase). NOT a kind -- a projection over ``SparcPhaseId`` + the
    reused ``pipeline_template`` (see module TAXONOMY NOTE). ``phase`` is one of the
    five ``SparcPhaseId`` values (the fixed methodology set, reused from
    orchestration -- typed as the Literal, NOT ``str``, because the SPARC phase set
    never extends); ``feature_id`` ties the phase to its feature
    (``features/<name>/sparc/``, 04 P1 #1); ``gate_status`` is the explicit
    phase-gate verdict to advance (04 FR-002, e.g. ``open`` / ``passed`` /
    ``blocked``); ``content`` is the phase artifact body. A Code-phase artifact
    traces back to a Specification requirement via ``traces_to: SPEC.req-N`` carried
    in ``content`` (04 P1 #3)."""

    phase: SparcPhaseId
    feature_id: str
    gate_status: str
    content: str


@dataclass(frozen=True, slots=True)
class SparcTemplate:
    """The scaffold template for one SPARC phase (04 US P1 / FR-001/002). NOT a kind
    -- it references the reused ``pipeline_template`` that backs the 5-phase
    pipeline. ``phase`` is one of ``SparcPhaseId``; ``pipeline_template_id`` is the
    id of the ``pipeline_template`` instance this phase belongs to (the founder-rule
    reuse anchor); ``gate_criteria`` is the ordered tuple of quality criteria that
    must hold to advance to the next phase (04 FR-002 explicit gates);
    ``content_template`` is the template body scaffolded into
    ``features/<name>/sparc/`` (04 P1 #1), from which the next phase pre-populates
    >= 30% of its fields (04 P1 #2 / V04-F6)."""

    phase: SparcPhaseId
    pipeline_template_id: str
    gate_criteria: tuple[str, ...] = ()
    content_template: str = ""


# --------------------------------------------------------------------------- #
# Protocols -- the seams the impl waves implement. Structural (no base class     #
# required); runtime_checkable allows isinstance smoke checks. Each maps to a    #
# contract test signature frozen in tests/distribution/contract.                 #
# --------------------------------------------------------------------------- #
@runtime_checkable
class SkillInstaller(Protocol):
    """The cross-agent skill-install seam (13 US P1 / FR-001/003/005; 10 US P2).
    ``install`` resolves ``skill_ref`` through the ordered ``sources`` (the first
    that resolves wins -- a configured ``custom_registry`` before the public
    ``registry``, 10 P2 #2) and returns a typed ``InstallPlan`` (resolved source +
    pinned tree SHA + per-detected-agent target dirs) from which the
    round-trip-stable ``Lockfile`` / ``LockEntry`` is written (13 SC-001/002). A
    deleted source raises ``SkillSourceUnavailableError`` and leaves the lockfile
    untouched (13 E1); a ``--frozen`` SHA drift raises ``LockfileMismatchError`` (13
    SC-002). The impl wave ships the concrete CLI-backed installer
    (``cexai skills add``) behind ``@vercel/detect-agent``; the contract test
    ``test_skill_installer_plans`` drives it RED->GREEN."""

    def install(self, skill_ref: str, sources: tuple[str, ...]) -> InstallPlan:
        """Resolve ``skill_ref`` across ``sources`` into a typed ``InstallPlan``."""
        ...


@runtime_checkable
class SkillVerifier(Protocol):
    """The cross-runtime parity seam (10 US P3 / FR-003 / SC-003; 13 SC-004).
    ``verify`` executes a skill's claimed runtimes and returns a typed
    ``CrossRuntimeReport`` (parity + the diverging ``failures`` set). A skill that
    claims no runtimes (empty ``runtime_compatibility``) is exempt and returns
    ``parity == True`` with no runtimes exercised (the V10-F2 bar). The report is
    ADVISORY -- a failure flags maintainer review, it does NOT auto-demote (V10-F3);
    the publish gate is what raises ``CrossRuntimeParityError`` for a cross-runtime-
    claiming skill that fails. The impl wave ships the concrete verifier (Claude +
    Ollama minimum) per ADR 013 Article XIV; the contract test
    ``test_skill_verifier_cross_runtime`` drives it."""

    def verify(self, skill: SkillManifest) -> CrossRuntimeReport:
        """Execute ``skill`` across its claimed runtimes and return a parity report."""
        ...


@runtime_checkable
class SparcMethodology(Protocol):
    """The opt-in SPARC methodology seam (04 US P1 / FR-001/002). ``template``
    returns the typed ``SparcTemplate`` scaffold for a ``SparcPhaseId`` (the 5-phase
    templates with explicit gates, FR-001/002); ``advance`` moves a feature into a
    phase, evaluating the prior phase's gate, and returns the resulting typed
    ``SparcPhase`` projection -- a failed gate raises ``SparcGateError`` and the
    phase does not advance. A non-algorithmic feature triggers a non-fatal
    ``SPARC_MISFIT`` warning suggesting spec-kit instead (04 edge case), it does not
    block. The impl wave ships the concrete methodology over the reused
    ``pipeline_template``; the contract test ``test_sparc_methodology_advances``
    drives it RED->GREEN."""

    def template(self, phase: SparcPhaseId) -> SparcTemplate:
        """Return the typed ``SparcTemplate`` scaffold for ``phase``."""
        ...

    def advance(self, feature_id: str, phase: SparcPhaseId) -> SparcPhase:
        """Advance ``feature_id`` into ``phase`` (gating the prior) and return it."""
        ...
