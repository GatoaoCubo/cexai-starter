---
id: p12_ct_product_launch.md
kind: crew_template
8f: F2_become
pillar: P12
llm_function: CALL
crew_name: product_launch
purpose: Coordinate a 4-role crew that ships a new product launch package -- positioning, copy, assets, and QA gate
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "researcher -> copywriter -> designer -> qa"
handoff_protocol_id: a2a-task-sequential
quality: null
keywords: [a2a task, artifact, quality score, handoff protocol, sequential process, instance id, regression check, crew instance]
density_score: 1.0
title: "Product Launch Crew Template"
version: "1.0.0"
author: n02_marketing
tags: [crew_template, product_launch, marketing, composable]
tldr: "4-role sequential crew: market intel -> positioning copy -> visual assets -> QA gate"
domain: "product launch orchestration"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p02_ra_market_researcher.md
  - p02_ra_copywriter.md
  - p02_ra_designer.md
  - p02_ra_qa_reviewer.md
  - team_charter_launch_template.md
---

## Overview
Instantiate when a product or feature needs a cross-function launch package.
Producer is the marketing nucleus; consumers are sales/growth. The crew runs
four roles in strict sequence; each emits a deliverable that the next role
grounds on. Handoff is via a2a Task with artifact attached.

This is the flagship example of the **composable-crew** pattern: `crew_template`
(this file) + `role_assignment` (4 files) + `team_charter` (1 instance-specific
contract). See `crew_template`'s own kind documentation for how the 3 pieces
compose, and for grid-of-crews (running several instances of this crew in
parallel against different charters).

## Roles
| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| market_researcher | p02_ra_market_researcher.md | Scan market + competitors, produce positioning brief |
| copywriter | p02_ra_copywriter.md | Turn brief into launch copy (tagline, headline, body) |
| designer | p02_ra_designer.md | Compose visual assets spec (hero, social, email header) |
| qa_reviewer | p02_ra_qa_reviewer.md | Enforce the quality gate on every deliverable |

## Process
Topology: `sequential`. Rationale: each role strictly depends on the previous
artifact. Parallelism adds no value and introduces consistency risk
(copywriter needs positioning; designer needs copy; QA needs all three).

## Memory Scope
| Role | Scope | Retention |
|------|-------|-----------|
| market_researcher | shared | persistent (knowledge_card saved to P01) |
| copywriter | shared | per-crew-instance |
| designer | shared | per-crew-instance |
| qa_reviewer | shared | per-crew-instance + regression_check archive |

## Handoff Protocol
`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. Next role reads prior artifact before
starting its own F1 CONSTRAIN.

## Success Criteria
- [ ] All 4 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] Every deliverable clears the charter's quality_gate (QA-attested)
- [ ] Handoff protocol signals present for 4/4 roles
- [ ] No role produced an artifact without reading upstream output

## Instantiation
```bash
python _tools/cex_crew.py run product_launch \
  --charter N02_marketing/P12_orchestration/crews/team_charter_launch_template.md
```

Copy `team_charter_launch_template.md` to a mission-specific charter first and
fill its `{{open_vars}}` (product name, target audience, deadline, budget) --
never run the crew against the bare template.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_market_researcher.md]] | downstream | 0.50 |
| [[p02_ra_copywriter.md]] | downstream | 0.46 |
| [[p02_ra_designer.md]] | downstream | 0.43 |
| [[p02_ra_qa_reviewer.md]] | downstream | 0.40 |
| [[team_charter_launch_template.md]] | related | 0.35 |
