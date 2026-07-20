---
id: p12_ct_research_sprint
kind: crew_template
pillar: P12
llm_function: CALL
crew_name: research_sprint
purpose: "Coordinate a 3-role crew that turns a research intake into a validated intelligence brief -- scout gathers raw sourced findings, analyst structures and validates them, synthesizer produces the final brief"
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "scout -> analyst -> synthesizer"
handoff_protocol_id: a2a-task-sequential
quality: null
keywords: [a2a task, artifact, quality score, handoff protocol, sequential process, instance id, research brief]
density_score: 0.92
title: "Research Sprint Crew Template"
version: "1.0.0"
author: n01_intelligence
tags: [crew_template, research_sprint, intelligence, composable]
tldr: "3-role sequential crew: scout -> analyst -> synthesizer. Turns any research intake into a source-grounded, quality-gated intelligence brief."
domain: "research department orchestration"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p02_ra_scout
  - p02_ra_analyst
  - p02_ra_synthesizer
  - p12_tc_research_sprint_v1
  - p06_is_n01
---

## Overview

Instantiate when N01 needs a full research pass on a topic -- not just a
single search, but a sourced, cross-checked, synthesized brief. Producer is
N01 (intelligence); consumers are any nucleus that requested the research via
the `p06_is_n01.md` intake contract. The crew runs three roles in strict
sequence; each emits a `knowledge_card` that the next role grounds on.
Handoff is via a2a Task with artifact attached.

This is the general-purpose research crew for the department. For a
narrower, competitor-focused variant, add a second crew_template that reuses
the same `scout`/`analyst` roles with a tighter charter -- the roles are
already generic enough to support that without change.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| scout | p02_ra_scout.md | Cast a wide net across sources, produce a sourced raw-findings KC |
| analyst | p02_ra_analyst.md | Structure and validate the scout's findings, extract patterns and gaps |
| synthesizer | p02_ra_synthesizer.md | Cross-reference everything, produce the final quality-gated brief |

## Process

Topology: `sequential`. Rationale: each role strictly depends on the
previous artifact. The analyst cannot structure findings that do not exist
yet; the synthesizer cannot cross-reference an analysis that has not been
produced. Parallelism adds no value here and would let the synthesizer see
raw, unvalidated data.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| scout | shared | persistent (knowledge_card saved to P01) |
| analyst | shared | per-crew-instance |
| synthesizer | shared | per-crew-instance |

## Handoff Protocol

`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. The next role reads the prior artifact
before starting its own F1 CONSTRAIN.

## Quality Gate

Every role's output is checked against `p11_qg_research_n01.md` before
handoff. The synthesizer's final brief must additionally satisfy the
`quality_gate` value declared in the instantiating `team_charter`
(`p12_tc_research_sprint_v1.md` -- default recommendation 8.5).

## Success Criteria

- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] Every deliverable clears the hard gates in `p11_qg_research_n01.md`
- [ ] Handoff protocol signals present for 3/3 roles
- [ ] No role produced an artifact without reading upstream output
- [ ] Final brief follows the `p03_pt_research_brief.md` output structure

## Instantiation

```bash
python _tools/cex_crew.py run research_sprint \
    --charter N01_intelligence/P12_orchestration/p12_tc_research_sprint_v1.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_scout]] | child | 0.55 |
| [[p02_ra_analyst]] | child | 0.55 |
| [[p02_ra_synthesizer]] | child | 0.55 |
| [[p12_tc_research_sprint_v1]] | related | 0.42 |
| [[p06_is_n01]] | upstream | 0.30 |
