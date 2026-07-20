---
id: team_charter_subscription_design
kind: team_charter
pillar: P12
nucleus: n06
llm_function: GOVERN
charter_id: subscription_design_template
crew_template_ref: p12_ct_subscription_design.md
mission_statement: "Design a complete subscription tier model: segment research + tier architecture + retention validation for {{PRODUCT_NAME}} -- ready for {{LAUNCH_CONTEXT}}."
quality_gate: 9.0
deadline: "{{DEADLINE_ISO8601}}"
deliverables:
  - "Segment profile (P01) -- >= 3 segments with TAM, WTP, usage patterns, churn risk"
  - "Tier model (P11) -- >= 3 tiers with pricing, feature gates, value metrics, annual discount"
  - "Retention playbook (P11/P07) -- churn prevention triggers + NRR projections + win-back sequence"
budget:
  tokens: "{{TOKEN_BUDGET}}"
  wall_clock_seconds: "{{WALL_CLOCK_BUDGET}}"
  usd: "{{USD_BUDGET}}"
stakeholders:
  - "{{BRAND_NAME}}"
  - "n07_orchestrator"
  - "n06_commercial"
escalation_protocol: "If any role crosses its budget ceiling or fails 3 consecutive quality checks, emit signal_{role}_escalate.json to .cex/runtime/signals/. N07 reads it and either extends budget or kills the crew."
termination_criteria: "ANY of: (1) retention_analyst signals subscription-design-complete with quality >= 9.0; (2) budget exhausted; (3) deadline passed; (4) 3 consecutive quality rejects on the same artifact."
quality: null
title: "Team Charter TEMPLATE -- Subscription Design"
version: "1.0.0"
tags: [team_charter, subscription_design, commercial, template, n06]
tldr: "TEMPLATE -- instantiate by filling every {{open_var}}. Default mission contract for the subscription_design crew: segment research -> tier architecture -> retention validation in 3 sequential roles."
domain: "subscription tier design governance"
related:
  - p12_ct_subscription_design
  - p02_ra_segment_researcher
  - p02_ra_tier_architect
  - p02_ra_retention_analyst
  - subscription_tier_n06
updated: "2026-07-20"
---

## How to instantiate this template

This file is a TEMPLATE, not an instance -- do not run it as-is. Copy it,
fill every `{{open_var}}`, drop the word "template" from the new
`charter_id` and filename (e.g. `team_charter_subscription_design_launch01.md`),
then run:

```bash
python _tools/cex_crew.py run subscription_design \
    --charter N06_commercial/P12_orchestration/crews/team_charter_subscription_design_<instance>.md \
    --execute
```

## Mission Statement

Design a complete subscription tier model for `{{PRODUCT_NAME}}`. Owner: N06
(commercial). Consumer: `{{LAUNCH_CONTEXT}}` (new launch | pricing change |
tier redesign).

## Deliverables

1. Segment profile (P01) -- >= 3 customer segments with TAM, WTP, usage patterns, churn risk
2. Tier model (P11) -- >= 3 tiers with pricing, feature gates, value metrics, and annual discount structure -- see [[subscription_tier_n06]] for the target shape
3. Retention playbook (P11/P07) -- churn prevention triggers, NRR projections (3 scenarios), win-back sequence

## Success Metrics

- Each deliverable quality >= 9.0 (peer-reviewed, never self-scored)
- Wall-clock under `{{WALL_CLOCK_BUDGET}}` seconds for the full crew
- Token budget under `{{TOKEN_BUDGET}}` total
- All 3 a2a-task handoff signals present, in order
- NRR projection base scenario >= 110%
- No tier cannibalization (each adjacent tier pair clears `{{MIN_UPGRADE_UPLIFT_PCT}}`% value uplift)

## Budget

- Tokens: `{{TOKEN_BUDGET}}` (hard ceiling)
- Wall-clock: `{{WALL_CLOCK_BUDGET}}` seconds
- USD: `{{USD_BUDGET}}`

## Stakeholders

- `{{BRAND_NAME}}` (product owner -- decides WHAT)
- n07_orchestrator (dispatches + monitors + consolidates)
- n06_commercial (nucleus that owns the crew instance)

## Escalation Protocol

If any role crosses its budget ceiling or fails 3 consecutive quality
checks, emit `signal_{role}_escalate.json` to `.cex/runtime/signals/`. N07
reads it and either extends the budget (if justified) or terminates the
crew with partial results.

## Termination Criteria

ANY of:
1. `retention_analyst` signals `subscription-design-complete` with quality >= 9.0
2. Token or wall-clock budget exhausted
3. `{{DEADLINE_ISO8601}}` passed
4. 3 consecutive quality rejects on the same artifact (stuck loop)

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p12_ct_subscription_design]] | parent |
| [[p02_ra_segment_researcher]] | upstream |
| [[p02_ra_tier_architect]] | upstream |
| [[p02_ra_retention_analyst]] | upstream |
