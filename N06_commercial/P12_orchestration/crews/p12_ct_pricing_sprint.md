---
id: p12_ct_pricing_sprint
kind: crew_template
8f: F2_become
pillar: P12
nucleus: n06
llm_function: CALL
crew_name: pricing_sprint
purpose: "Coordinate a 3-role crew that researches the market, models a tier structure, and validates the offer before any price is published"
process: sequential
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "market_researcher -> pricing_modeler -> offer_validator"
handoff_protocol_id: a2a-task-sequential
quality: null
tags: [crew_template, pricing_sprint, commercial, composable, n06]
title: "Pricing Sprint Crew Template"
version: "1.0.0"
tldr: "3-role sequential crew: market research -> tier modeling -> offer validation. Encodes the RACI rule 'N06 never prices without market research (N01 dependency)' as a hard sequencing gate, not a suggestion."
domain: "pricing model design and validation"
created: "2026-07-20"
related:
  - p02_ra_market_researcher
  - p02_ra_pricing_modeler
  - p02_ra_offer_validator
  - p06_enum_pricing_tiers_n06
  - subscription_tier_n06
---

# Pricing Sprint Crew Template

## Overview

Instantiate before publishing or changing a price. Owner is N06
(commercial); N01 (intelligence) is a hard upstream dependency, not an
optional consult. Three roles run in strict sequence: `market_researcher`
grounds the sprint in real competitive and willingness-to-pay signal,
`pricing_modeler` designs the tier structure and feature gates, and
`offer_validator` stress-tests the resulting offer with a transparent ROI
proof before anything ships. Handoff is via a2a Task with artifact attached
-- the same protocol as [[p12_ct_product_launch]] in N02.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| market_researcher | p02_ra_market_researcher.md | Operationalizes the RACI rule "N06 never prices without market research (N01 dependency)" -- produces the competitive_matrix that gates every downstream step |
| pricing_modeler | p02_ra_pricing_modeler.md | Turns the competitive matrix into a tier structure, feature-gate matrix, and discount rules |
| offer_validator | p02_ra_offer_validator.md | Builds a transparent ROI proof for the modeled offer and checks for cannibalization before publish |

## Process

Topology: `sequential`. Rationale: `pricing_modeler` cannot design tiers
without the competitive matrix, and `offer_validator` cannot prove value
without a finished tier model. This is not a style choice -- it is the RACI
dependency chain made executable. The RACI matrix's Explicit Prohibitions
state plainly: **"N06 NEVER prices without market research (N01
dependency)"** (`.claude/rules/raci-matrix.md`, mirrored in
`.claude/rules/n07-orchestrator.md`). A crew that runs `pricing_modeler`
before `market_researcher` completes is a RACI violation, not merely a
quality risk -- the sequential topology is what makes that violation
structurally impossible rather than just discouraged.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| market_researcher | shared | persistent (competitive_matrix saved to P01) |
| pricing_modeler | shared | per-crew-instance |
| offer_validator | shared | per-crew-instance + archive in P07 |

## Handoff Protocol

`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. The next role reads the prior artifact
before starting its own F1 CONSTRAIN. `pricing_modeler` MUST refuse to start
if no upstream `market_researcher` signal exists.

## Success Criteria

- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] Every deliverable quality >= 9.0 (peer-reviewed, never self-scored)
- [ ] Handoff signals present for 3/3 roles, in order
- [ ] `pricing_modeler`'s tier model cites the `market_researcher` artifact by path
- [ ] `offer_validator`'s ROI proof is transparent (every input visible, never a black-box number)
- [ ] No role produced an artifact without reading its upstream role's output

## Instantiation

```bash
python _tools/cex_crew.py run pricing_sprint \
    --charter N06_commercial/P12_orchestration/team_charter_pricing_sprint.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p02_ra_market_researcher]] | child |
| [[p02_ra_pricing_modeler]] | child |
| [[p02_ra_offer_validator]] | child |
| [[p06_enum_pricing_tiers_n06]] | related |
| [[subscription_tier_n06]] | related |
