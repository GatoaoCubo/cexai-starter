"""CEXAI distribution layer -- the v0.5 packaging + methodology plane.

Two distribution subsystems share one frozen vocabulary
(``cexai.distribution._shared.types``):

  skills  agentskills.io packaging + cross-agent install + cross-runtime verify  -- 10_skills-sh + 13_vercel-skills
  sparc   opt-in 5-phase SPARC methodology (Specification..Code) templates       -- 04_claude-flow

Import is intentionally light (Article VIII): this module exposes nothing at the
top level for W0. The subsystems stay addressable at ``cexai.distribution.
{skills,sparc}`` once their impl-wave implementations land. Every subsystem
COMPOSES with the existing substrate -- the SPARC projection REUSES the v0.3
orchestration ``SparcPhaseId`` and the existing ``pipeline_template`` kind; the
skills installer emits a ``reasoning_trace`` (13 FR-012) and validates installed
frontmatter against ``.cex/kinds_meta.json`` (13 FR-013) -- and does NOT replace
any of it.

TAXONOMY NOTE (founder rule, taxonomy-neutral wave): the types frozen here are
Python CODE. This wave -- and the whole v0.5 milestone -- registers ZERO kinds and
does NOT touch ``.cex/kinds_meta.json`` (see
cexai/docs/adr_v05_distribution_taxonomy.md). ``sparc_phase`` (04 FR-005's "new
top-level kind") is REJECTED -> the 5 SPARC phases REUSE ``pipeline_template``;
``skill`` (10) reuses the existing ``skill`` kind; ``skill_registry`` reuses
``marketplace_app_manifest``; ``MethodologyChoice`` reuses ``decision_record``;
``reasoning_trace`` (13) reuses the existing kind. Lockfile / InstallPlan /
SparcPhase etc. are RUNTIME DATACLASSES, not kinds.

Spec provenance: cexai-specs/10_skills-sh, /13_vercel-skills, /04_claude-flow
(US + FR + SC + Key Entities per subsystem).

absorbs: 10_skills-sh + 13_vercel-skills + 04_claude-flow
"""

__all__: list = []
