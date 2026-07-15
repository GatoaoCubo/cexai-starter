"""Spec-kit scaffold templates (cexai-specs/01_spec-kit absorption) -- ASCII constants.

The five Spec-Driven Development artifacts spec-kit defines
(Constitution -> Spec -> Plan -> Tasks -> Analyze). CEX absorbed spec-kit as its
working methodology (cexai-specs/01_spec-kit/retro.md, "the methodology IS the
deliverable"); this module mirrors the artifact STRUCTURE as ASCII string constants
so the thin ``cexai spec-kit init|spec|plan|tasks`` scaffolders can emit a starting
point offline (Article XIV -- no network, no LLM).

Founder rule (taxonomy-neutral): these are CODE string constants, NOT new kinds.
The artifacts reuse EXISTING kinds per the 01_spec-kit retro mapping table --
Constitution -> ``axiom`` + ``constitutional_rule``; Spec -> ``decision_record``;
Plan -> ``mission_plan`` convention; Tasks -> ``handoff`` convention. Analyze is a
CHECKER (code, see ``analyze.py``), not a kind. No ``.cex/kinds_meta.json`` edit.

Per Article XIX every emitted artifact declares an ``open_vars:`` block in its
frontmatter (empty until a compiler/nucleus fills it during F1/F3). ASCII-only per
the repo's executable-code rule -- ``--`` for em-dash, ``->`` for arrows.

absorbs: 01_spec-kit
"""

from __future__ import annotations

__all__ = [
    "TEMPLATE_NAMES",
    "TEMPLATES",
    "CONSTITUTION_TEMPLATE",
    "SPEC_TEMPLATE",
    "PLAN_TEMPLATE",
    "TASKS_TEMPLATE",
    "ANALYZE_TEMPLATE",
    "emit",
]


# --------------------------------------------------------------------------- #
# Constitution -- the governing law (reuses axiom + constitutional_rule). The   #
# inherited project constitution lives at cexai-specs/_decisions/constitution.md#
# (17+ articles); this template is the per-project override scaffold.           #
# --------------------------------------------------------------------------- #
CONSTITUTION_TEMPLATE = """\
# <project> Constitution

> The governing law of <project>. Inherit the base articles; override only what
> this project must change. Adapted from github/spec-kit (MIT).

**Version**: 0.1.0
**Ratified**: <date>

---

## Core Articles (inherited unless overridden)

### Article I -- Library-First
Every feature begins as a standalone library; applications are thin orchestrators.

### Article II -- CLI Interface Mandate
Every feature exposes text I/O, a `--json` structured mode, and logs to stderr.

### Article III -- Test-First (TDD)
No implementation code before a test is written and observed to FAIL.

### Article VII -- Simplicity Over Cleverness
Maximum 3 projects per initial implementation. No speculative future-proofing.

### Article XI -- Type-First Artifacts
Every output is `frontmatter + body`; frontmatter declares `kind` and `quality`.

### Article XVI -- Spec-Kit Native
Every feature ships Constitution -> Spec -> Plan -> Tasks -> Analyze.

---

## Project Overrides

| Article | Override | Rationale |
|---------|----------|-----------|
| <none>  |          |           |

---

## Amendment Process
1. Propose via ADR. 2. Peer review (target >= 9.0). 3. Bump version. 4. Re-run analyze.
"""


# --------------------------------------------------------------------------- #
# Spec -- User Stories P1/P2/P3 + FR-### + SC-### + Given/When/Then.            #
# --------------------------------------------------------------------------- #
SPEC_TEMPLATE = """\
---
kind: specification
open_vars: []
---

# <feature> -- Specification

**Feature Branch**: `<NNN-feature-name>`
**Created**: <date>
**Status**: Draft
**Owner nucleus**: <N0X (sin lens)>

---

## 1. User Scenarios & Testing

### User Story P1 -- <highest-value capability>

**As a** <role>
**I want** <capability>
**So that** <outcome>.

**Why this priority**: <reason this is P1>.

**Independent Test**: <one observable end-to-end check that proves P1 alone>.

**Acceptance Scenarios**:
1. **Given** <state>, **When** <action>, **Then** <observable result>.

### User Story P2 -- <next capability>

**As a** <role> **I want** <capability> **So that** <outcome>.

**Acceptance Scenarios**:
1. **Given** <state>, **When** <action>, **Then** <observable result>.

### User Story P3 -- <designed-in / future-proofing capability>

**As a** <role> **I want** <capability> **So that** <outcome>.

**Acceptance Scenarios**:
1. **Given** <state>, **When** <action>, **Then** <observable result>.

---

## 2. Requirements

### Functional Requirements
- **FR-001**: System MUST <observable behavior>.
- **FR-002**: System MUST <observable behavior>.
- **FR-003**: System MUST <observable behavior>.

### Key Entities
- **<Entity>**: REUSE existing kind `<kind>` OR justify a NEW kind via ADR.

---

## 3. Success Criteria
- **SC-001**: <measurable outcome with a baseline>.
- **SC-002**: <measurable outcome with a baseline>.

---

## 4. Clarifications Needed

Mark any unresolved question inline with `[NEEDS CLARIFICATION: <question>]`.
(0 markers remain when the spec is ready for Plan.)

---

## Prior Art
- <alternative 1 considered and why rejected>.
- <alternative 2 considered and why rejected>.
- <alternative 3 considered and why rejected>.
"""


# --------------------------------------------------------------------------- #
# Plan -- 8-row Technical Context + Constitution Check + Complexity Tracking.   #
# --------------------------------------------------------------------------- #
PLAN_TEMPLATE = """\
---
kind: plan
open_vars: []
---

# <feature> -- Implementation Plan

**Spec**: `<feature>/spec.md`
**Status**: Draft

---

## Summary
<one paragraph: what ships, and that the libraries are independently shippable>.

---

## Technical Context

| # | Decision | Value | Rationale |
|---|----------|-------|-----------|
| 1 | Language/Version    | <e.g. Python 3.11> | <why> |
| 2 | Primary Dependencies| <libs>             | <why> |
| 3 | Storage             | <store>            | <why> |
| 4 | Testing             | <framework>        | <why> |
| 5 | Platform            | <target>           | <why> |
| 6 | Project Type        | <N libraries>      | Article VII cap |
| 7 | Performance         | <targets>          | per SCs |
| 8 | Constraints         | <hard constraints> | per SCs |

---

## Constitution Check

| Gate | Pass? | Notes |
|------|-------|-------|
| Simplicity (VII)       | YES |  |
| Anti-Abstraction (VIII)| YES |  |
| Library-First (I)      | YES |  |
| Test-First (III)       | YES |  |
| Type-First (XI)        | YES |  |
| Spec-Kit (XVI)         | YES |  |

Coverage: this plan addresses User Story P1, P2, and P3.

---

## Complexity Tracking
(Record any Constitution violation here, or leave empty.)

| Article violated | Why necessary | Simpler alternative rejected because |
|------------------|---------------|--------------------------------------|
| <none>           |               |                                      |
"""


# --------------------------------------------------------------------------- #
# Tasks -- [T###] [P] [US#] phased, tests-before-impl (Article III TDD).        #
# --------------------------------------------------------------------------- #
TASKS_TEMPLATE = """\
---
kind: tasks
open_vars: []
---

# <feature> -- Tasks

**Spec**: `<feature>/spec.md`
**Plan**: `<feature>/plan.md`

> Notation: `[T###]` id, `[P]` parallel-safe, `[US#]` the user story it serves,
> `[TDD]` a test that MUST be written failing first.

## Phase 1: Setup
- [ ] **T001** [P] [SETUP] <scaffold project skeleton>

## Phase 2: Foundational
- [ ] **T010** [FOUNDATIONAL] <define shared types / contracts>

## Phase 3: US1
### Tests first
- [ ] **T100** [P] [US1] [TDD] <test for FR-001> -- MUST FAIL
### Implementation
- [ ] **T110** [US1] <implement to satisfy T100 / FR-001>
### Verification
- [ ] **T120** [US1] Run T100 -- MUST PASS

## Phase 4: US2
- [ ] **T200** [P] [US2] [TDD] <test for FR-002> -- MUST FAIL
- [ ] **T210** [US2] <implement to satisfy T200 / FR-002>

## Phase 5: US3
- [ ] **T300** [P] [US3] [TDD] <test for FR-003> -- MUST FAIL
- [ ] **T310** [US3] <implement to satisfy T300 / FR-003>

## Phase N: Polish
- [ ] **T900** [P] [POLISH] <docs, benchmarks, portability>
"""


# --------------------------------------------------------------------------- #
# Analyze -- the cross-artifact report shape (the CHECKER lives in analyze.py). #
# --------------------------------------------------------------------------- #
ANALYZE_TEMPLATE = """\
---
kind: analysis
open_vars: []
---

# <feature> -- Cross-Artifact Analysis

**Status**: <PASS | CONDITIONAL | FAIL>

> This is the report SHAPE. Generate it with `cexai spec-kit analyze <feature_dir>`
> (the checker compares spec vs plan vs tasks; it does not hand-author this file).

## 1. Spec -> Plan coverage
| Spec requirement | Plan element | Status |
|------------------|--------------|--------|
| FR-001           | <module>     | OK     |

## 2. Spec -> Tasks traceability
| User Story | Tasks | Status |
|------------|-------|--------|
| US1        | T1xx  | OK     |

## 3. Ambiguity audit
| Location | Marker | Status |
|----------|--------|--------|
| <none>   |        |        |

## 4. Verdict
<PASS = no findings; CONDITIONAL = advisory findings only; FAIL = a critical/high finding>.
"""


# Canonical ordered scaffold set (Constitution -> Spec -> Plan -> Tasks -> Analyze).
TEMPLATE_NAMES: tuple[str, ...] = ("constitution", "spec", "plan", "tasks", "analyze")

TEMPLATES: dict[str, str] = {
    "constitution": CONSTITUTION_TEMPLATE,
    "spec": SPEC_TEMPLATE,
    "plan": PLAN_TEMPLATE,
    "tasks": TASKS_TEMPLATE,
    "analyze": ANALYZE_TEMPLATE,
}


def emit(name: str) -> str:
    """Return the ASCII scaffold template named ``name`` (one of ``TEMPLATE_NAMES``).

    Raises ``KeyError`` with the valid names for an unknown template, so the CLI can
    surface a precise diagnostic instead of an opaque miss."""
    try:
        return TEMPLATES[name]
    except KeyError:
        raise KeyError(
            f"unknown spec-kit template {name!r}; valid: {', '.join(TEMPLATE_NAMES)}"
        ) from None
