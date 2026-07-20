---
id: p12_ct_build_review
kind: crew_template
pillar: P12
llm_function: CALL
crew_name: build_review
purpose: "Coordinate a 3-role crew that builds one artifact, peer-reviews it against the quality gate, and integrates it cleanly (cross-references resolved, compiled, doctor-clean) before signaling complete"
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "builder -> reviewer -> integrator"
handoff_protocol_id: a2a-task-sequential
quality: null
title: "Build-Review-Integrate Crew Template"
version: "1.0.0"
author: crew-template-builder
tags: [crew_template, build_review, engineering, composable, peer_review]
tldr: "3-role sequential crew: builder produces one artifact via full 8F -> reviewer peer-scores it against the quality gate (never self-score) -> integrator resolves cross-references and confirms doctor-clean before signaling complete."
domain: "engineering build-review crew"
created: "2026-07-20"
keywords: [8f pipeline, peer review, quality gate, cross-reference, doctor-clean, a2a-task-sequential, never self-score]
density_score: 0.90
related:
  - p02_ra_build_review_builder
  - p02_ra_build_review_reviewer
  - p02_ra_build_review_integrator
  - p12_ct_cross_provider_council
  - p02_ra_council_judges
---

## Overview

Instantiate when a single artifact needs to go from intent to a published,
cross-referenced, doctor-clean file without a human reviewing every step.
Owner: N03 (engineering). Consumer: whoever holds the team_charter (a solo
operator, or an orchestrator dispatching this crew as one cell of a larger
mission). The crew runs three roles in strict sequence; each emits a
deliverable that the next role grounds on. Handoff is via a2a Task with
artifact attached.

The core discipline this crew enforces: **the builder never grades its own
work.** Per this project's constitution (`quality: null` -- never self-score;
peer review assigns quality), the reviewer role is bound to a read-only
scoring agent that cannot Write or Edit -- it can only score and reject. The
builder cannot pass its own artifact; only the reviewer's independent
judgment can.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| builder | p02_ra_build_review_builder.md | Produce the artifact end-to-end via the full 8F pipeline (F1-F8) |
| reviewer | p02_ra_build_review_reviewer.md | Peer-score the artifact against the charter's quality_gate; never self-score |
| integrator | p02_ra_build_review_integrator.md | Resolve cross-references, confirm doctor-clean, signal crew-complete |

## Process

Topology: `sequential`. Rationale: each role strictly depends on the
previous artifact -- the reviewer cannot score what does not exist yet, and
the integrator cannot cross-reference or compile an artifact that has not
passed review. Parallelism would let an unreviewed (or rejected) artifact
reach integration, defeating the entire purpose of the crew.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| builder | shared | per-crew-instance (artifact + 8F trace) |
| reviewer | isolated | per-crew-instance (review_report only; never sees builder's self-assessment, because there isn't one) |
| integrator | shared | per-crew-instance + consistency report archived to P01 |

## Handoff Protocol

`a2a-task-sequential` -- each role writes a completion signal to
`.cex/runtime/signals/` with `artifact_path` (or `review_report_path`) +
`role_name` + status fields. The reviewer reads the builder's artifact
before scoring; the integrator reads the reviewer's review_report before
starting cross-reference work.

## Success Criteria

- [ ] Builder deliverable exists with `quality: null` in frontmatter (self-scoring never occurs)
- [ ] Reviewer produced a review_report citing the specific gate(s) any rejection failed
- [ ] Artifact quality score set ONLY by the reviewer, never by the builder
- [ ] Score meets or exceeds the charter's `quality_gate` before the integrator proceeds
- [ ] All wikilinks in the final artifact resolve to files that actually exist
- [ ] Doctor check is clean on the final artifact (integrator-verified)
- [ ] 3/3 a2a-task handoff signals present in `.cex/runtime/signals/`

## Instantiation

```bash
python _tools/cex_crew.py run build_review \
    --charter N03_engineering/P12_orchestration/team_charter_build_review_template.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_build_review_builder]] | upstream | 0.44 |
| [[p02_ra_build_review_reviewer]] | upstream | 0.42 |
| [[p02_ra_build_review_integrator]] | upstream | 0.40 |
| [[p12_ct_cross_provider_council]] | sibling | 0.35 |
| [[p02_ra_council_judges]] | related | 0.30 |
