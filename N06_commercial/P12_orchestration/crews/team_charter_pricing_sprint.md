---
id: team_charter_pricing_sprint
kind: team_charter
pillar: P12
nucleus: n06
llm_function: GOVERN
charter_id: pricing_sprint_template
crew_template_ref: p12_ct_pricing_sprint.md
mission_statement: "Research the market, model a tier structure, and validate the offer for {{PRODUCT_NAME}} -- ready for {{LAUNCH_CONTEXT}}."
quality_gate: 9.0
deadline: "{{DEADLINE_ISO8601}}"
deliverables:
  - "Competitive matrix (P01) -- >= 3 competitors x >= 4 dimensions"
  - "Tier model (P11) -- >= 3 tiers with pricing, feature gates, discount rules"
  - "ROI validation report (P07) -- transparent proof + cannibalization check + stress-test"
budget:
  tokens: "{{TOKEN_BUDGET}}"
  wall_clock_seconds: "{{WALL_CLOCK_BUDGET}}"
  usd: "{{USD_BUDGET}}"
stakeholders:
  - "{{BRAND_NAME}}"
  - "n07_orchestrator"
  - "n06_commercial"
escalation_protocol: "If any role crosses its budget ceiling or fails 3 consecutive quality checks, emit signal_{role}_escalate.json to .cex/runtime/signals/. N07 reads it and either extends budget or kills the crew."
termination_criteria: "ANY of: (1) offer_validator signals pricing-sprint-complete with quality >= 9.0; (2) budget exhausted; (3) deadline passed; (4) 3 consecutive quality rejects on the same artifact."
quality: null
title: "Team Charter TEMPLATE -- Pricing Sprint"
version: "1.0.0"
tags: [team_charter, pricing_sprint, commercial, template, n06]
tldr: "TEMPLATE -- instantiate by filling every {{open_var}}. Default mission contract for the pricing_sprint crew: competitive matrix -> tier model -> ROI validation in 3 sequential roles."
domain: "pricing sprint governance"
created: "2026-07-20"
related:
  - p12_ct_pricing_sprint
  - p02_ra_market_researcher
  - p02_ra_pricing_modeler
  - p02_ra_offer_validator
  - subscription_tier_n06
---

## How to instantiate this template

This file is a TEMPLATE, not an instance -- do not run it as-is. Copy it,
fill every `{{open_var}}`, drop the word "template" from the new
`charter_id` and filename (e.g. `team_charter_pricing_sprint_launch01.md`),
then run:

```bash
python _tools/cex_crew.py run pricing_sprint \
    --charter N06_commercial/P12_orchestration/team_charter_pricing_sprint_<instance>.md \
    --execute
```

## Mission Statement

Research the market, model a tier structure, and validate the offer for
`{{PRODUCT_NAME}}`. Owner: N06 (commercial). Consumer:
`{{LAUNCH_CONTEXT}}` (new launch | pricing change | renewal-tier redesign).

## Deliverables

1. Competitive matrix (P01) -- >= 3 competitors x >= 4 dimensions (price, tiers, gates, positioning)
2. Tier model (P11) -- >= 3 tiers with pricing, feature gates, and discount structure -- see [[subscription_tier_n06]] for the target shape
3. ROI validation report (P07) -- transparent proof, cannibalization check, stress-test under >= 2 pessimistic levers

## Success Metrics

- Each deliverable quality >= 9.0 (peer-reviewed, never self-scored)
- Wall-clock under `{{WALL_CLOCK_BUDGET}}` seconds for the full crew
- Token budget under `{{TOKEN_BUDGET}}` total
- All 3 a2a-task handoff signals present, in order
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
1. `offer_validator` signals `pricing-sprint-complete` with quality >= 9.0
2. Token or wall-clock budget exhausted
3. `{{DEADLINE_ISO8601}}` passed
4. 3 consecutive quality rejects on the same artifact (stuck loop)

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p12_ct_pricing_sprint]] | parent |
| [[p02_ra_market_researcher]] | upstream |
| [[p02_ra_pricing_modeler]] | upstream |
| [[p02_ra_offer_validator]] | upstream |
