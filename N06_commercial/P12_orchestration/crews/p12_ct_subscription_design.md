---
id: p12_ct_subscription_design
kind: crew_template
pillar: P12
nucleus: n06
llm_function: CALL
crew_name: subscription_design
purpose: 3-role sequential crew that researches customer segments, designs subscription tiers, and validates retention -- producing a launch-ready tier model with churn prevention overlay
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "segment_researcher -> tier_architect -> retention_analyst"
handoff_protocol_id: a2a-task-sequential
quality: null
title: "Subscription Design Crew Template"
version: "1.0.0"
tags: [crew_template, subscription_design, commercial, composable, n06]
tldr: "3-role sequential: customer segments -> tier model + feature gates -> churn prevention + NRR validation"
domain: "subscription tier design and retention validation"
related:
  - p02_ra_segment_researcher
  - p02_ra_tier_architect
  - p02_ra_retention_analyst
  - p12_ct_pricing_sprint
  - subscription_tier_n06
updated: "2026-07-20"
---

# Subscription Design Crew Template

## Overview

Instantiate when N06 needs to design or redesign a subscription model from
scratch. Owner is N06 (commercial); consumers are product, finance, and
growth. Three roles run in strict sequence: `segment_researcher` profiles
customer segments and maps willingness-to-pay; `tier_architect` designs the
tier structure, feature gates, and pricing; `retention_analyst` stress-tests
for churn risk and produces intervention playbooks. The output is a
launch-ready tier model with built-in retention safeguards.

**RACI note (pricing dependency).** `tier_architect` sets `price_monthly` /
`price_annual` per tier. Per the RACI rule "N06 NEVER prices without market
research (N01 dependency)" (`.claude/rules/raci-matrix.md`, mirrored in
`.claude/rules/n07-orchestrator.md`), those figures should be grounded in
real competitive and willingness-to-pay signal, not invented from
`segment_researcher`'s profile alone. If no market research exists yet for
this product, run [[p12_ct_pricing_sprint]] first -- its `market_researcher`
role produces exactly that grounding -- and hand its `competitive_matrix_path`
to `tier_architect` as additional input alongside the segment profile.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| segment_researcher | p02_ra_segment_researcher.md | Profile >= 3 segments with TAM, WTP, usage patterns, and churn risk |
| tier_architect | p02_ra_tier_architect.md | Design tier structure, feature gates, value metrics, and annual discount |
| retention_analyst | p02_ra_retention_analyst.md | Validate NRR under 3 scenarios, produce churn prevention playbook |

## Process

Topology: `sequential`. Rationale: `tier_architect` requires segment
profiles before designing tiers; `retention_analyst` requires the complete
tier model before stress-testing. Each role grounds on the prior role's
artifact, ensuring coherent end-to-end output.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| segment_researcher | shared | persistent (KC saved to P01 under N06) |
| tier_architect | shared | per-crew-instance |
| retention_analyst | shared | per-crew-instance + archive in P07 |

## Handoff Protocol

`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. The next role reads the prior artifact
before starting its own F1 CONSTRAIN. No role begins without an upstream
signal confirming quality >= 9.0.

## Success Criteria

- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] Every deliverable quality >= 9.0 (peer-reviewed, never self-scored)
- [ ] Handoff protocol signals present for 3/3 roles
- [ ] Segment profile covers >= 3 segments with TAM, WTP, and churn risk
- [ ] Tier model has >= 3 tiers with no cannibalization (>= 25% value uplift per adjacent pair)
- [ ] NRR projection present for base + optimistic + pessimistic scenarios
- [ ] Churn prevention playbook covers >= 3 intervention triggers per tier

## Instantiation

```bash
python _tools/cex_crew.py run subscription_design \
    --charter N06_commercial/P12_orchestration/crews/team_charter_subscription_design.md
python _tools/cex_crew.py run subscription_design \
    --charter N06_commercial/P12_orchestration/crews/team_charter_subscription_design.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p02_ra_segment_researcher]] | child |
| [[p02_ra_tier_architect]] | child |
| [[p02_ra_retention_analyst]] | child |
| [[p12_ct_pricing_sprint]] | related (upstream market-research crew this one depends on for real prices) |
| [[subscription_tier_n06]] | related |
