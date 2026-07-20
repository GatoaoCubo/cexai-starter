---
id: p12_ct_sales_pipeline
kind: crew_template
pillar: P12
nucleus: n06
llm_function: CALL
crew_name: sales_pipeline
purpose: Coordinate a 3-role sequential crew that builds a complete B2B sales package -- market strategy, collateral, and closing plays
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "strategist -> content_producer -> closer"
handoff_protocol_id: a2a-task-sequential
quality: null
title: "Sales Pipeline Crew Template"
version: "1.0.0"
tags: [crew_template, sales_pipeline, commercial, composable, n06]
tldr: "3-role sequential crew: market strategy -> sales collateral -> closing playbook"
domain: "B2B sales pipeline orchestration"
related:
  - p02_ra_strategist
  - p02_ra_content_producer
  - p02_ra_closer
  - p12_ct_pricing_sprint
  - p12_ct_subscription_design
updated: "2026-07-20"
---

# Sales Pipeline Crew Template

## Overview

Instantiate when N06 needs a complete B2B sales enablement package for a
product, tier, or market segment. Owner is N06 (commercial). The crew runs
three roles in strict sequence; each role emits a deliverable that grounds
the next. Handoff is via a2a Task with artifact attached. Outputs feed
sales ops, growth, and renewal teams directly.

**RACI note (pricing dependency).** `strategist` defines pricing tiers as
part of its strategy brief. Per the RACI rule "N06 NEVER prices without
market research (N01 dependency)" (`.claude/rules/raci-matrix.md`), ground
those tiers in real competitive and willingness-to-pay signal -- do not
invent them from segmentation alone. If no market research exists yet, run
[[p12_ct_pricing_sprint]] first (its `market_researcher` role produces
exactly that grounding) and feed its `competitive_matrix_path` into this
crew's `strategist` role as additional input.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| strategist | p02_ra_strategist.md | Analyze market segments, define pricing tiers, map customer journey + ICP |
| content_producer | p02_ra_content_producer.md | Produce sales collateral: pitch deck outline, case study template, ROI calculator |
| closer | p02_ra_closer.md | Build objection handling playbook, renewal workflow, expansion plays |

## Process

Topology: `sequential`. Rationale: strict dependency chain -- content_producer
needs the strategist's segment + pricing map before producing collateral;
closer needs the collateral pack before authoring objection plays.
Sequential ensures every downstream role is grounded on upstream artifact.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| strategist | shared | persistent (KC saved to P01 under N06) |
| content_producer | shared | per-crew-instance |
| closer | shared | per-crew-instance + archive in P05 |

## Handoff Protocol

`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. Next role reads prior artifact before
starting its own F1 CONSTRAIN. No role begins without an upstream signal
confirming quality >= 9.0.

## Success Criteria

- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] Every deliverable quality >= 9.0 (peer-reviewed, never self-scored)
- [ ] Handoff protocol signals present for 3/3 roles
- [ ] No role produced an artifact without reading upstream output
- [ ] Closer playbook covers >= 5 objection types + 1 expansion play

## Instantiation

```bash
python _tools/cex_crew.py run sales_pipeline \
    --charter N06_commercial/P12_orchestration/crews/team_charter_sales_pipeline.md
python _tools/cex_crew.py run sales_pipeline \
    --charter N06_commercial/P12_orchestration/crews/team_charter_sales_pipeline.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p02_ra_strategist]] | child |
| [[p02_ra_content_producer]] | child |
| [[p02_ra_closer]] | child |
| [[p12_ct_pricing_sprint]] | related (upstream market-research crew this one depends on for real prices) |
| [[p12_ct_subscription_design]] | sibling |
