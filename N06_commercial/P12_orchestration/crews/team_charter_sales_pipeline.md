---
id: team_charter_sales_pipeline
kind: team_charter
pillar: P12
nucleus: n06
llm_function: GOVERN
charter_id: sales_pipeline_template
crew_template_ref: p12_ct_sales_pipeline.md
mission_statement: "Build a complete B2B sales pipeline package for {{PRODUCT_NAME}}'s primary tier: strategy brief + collateral pack + closing playbook."
quality_gate: 9.0
deadline: "{{DEADLINE_ISO8601}}"
deliverables:
  - "Strategy brief (P01) -- market segments + pricing tiers + ICP + customer journey"
  - "Collateral pack (P05) -- pitch deck outline + case study template + ROI calculator"
  - "Closing package (P05) -- objection playbook + renewal workflow + expansion plays"
budget:
  tokens: "{{TOKEN_BUDGET}}"
  wall_clock_seconds: "{{WALL_CLOCK_BUDGET}}"
  usd: "{{USD_BUDGET}}"
stakeholders:
  - "{{BRAND_NAME}}"
  - "n07_orchestrator"
  - "n06_commercial"
escalation_protocol: "If any role crosses budget ceiling or fails 3 consecutive quality checks, emit signal_{role}_escalate.json to .cex/runtime/signals/. N07 reads and either extends budget or kills crew."
termination_criteria: "ANY of: (1) closer signals pipeline-complete with quality >= 9.0; (2) budget exhausted; (3) deadline passed; (4) 3 consecutive quality rejects on same artifact."
quality: null
title: "Team Charter TEMPLATE -- Sales Pipeline"
version: "1.0.0"
tags: [team_charter, sales_pipeline, commercial, template, n06]
tldr: "TEMPLATE -- instantiate by filling every {{open_var}}. Default mission contract for the sales_pipeline crew: strategy -> collateral -> closing in 3 sequential roles."
domain: "B2B sales pipeline governance"
related:
  - p12_ct_sales_pipeline
  - p02_ra_strategist
  - p02_ra_content_producer
  - p02_ra_closer
updated: "2026-07-20"
---

## How to instantiate this template

This file is a TEMPLATE, not an instance -- do not run it as-is. Copy it,
fill every `{{open_var}}`, drop the word "template" from the new
`charter_id` and filename (e.g. `team_charter_sales_pipeline_launch01.md`),
then run:

```bash
python _tools/cex_crew.py run sales_pipeline \
    --charter N06_commercial/P12_orchestration/crews/team_charter_sales_pipeline_<instance>.md \
    --execute
```

## Mission Statement

Build a complete B2B sales pipeline package for `{{PRODUCT_NAME}}`'s
primary tier. Owner: N06 (commercial). Consumer: sales ops, growth, and
renewal teams.

## Deliverables

1. Strategy brief (P01) -- market segments + pricing tiers + ICP + customer journey map
2. Collateral pack (P05) -- pitch deck outline + case study template + ROI calculator
3. Closing package (P05) -- objection handling playbook + renewal workflow + expansion plays

## Success Metrics

- Each deliverable quality >= 9.0 (peer-reviewed, never self-scored)
- Wall-clock under `{{WALL_CLOCK_BUDGET}}` seconds for the full crew
- Token budget under `{{TOKEN_BUDGET}}` total
- All 3 a2a-task handoff signals present
- Closing package covers >= 5 objection types + >= 2 expansion plays per tier

## Budget

- Tokens: `{{TOKEN_BUDGET}}` (hard ceiling)
- Wall-clock: `{{WALL_CLOCK_BUDGET}}` seconds
- USD: `{{USD_BUDGET}}`

## Stakeholders

- `{{BRAND_NAME}}` (product owner -- decides WHAT)
- n07_orchestrator (dispatches + monitors + consolidates)
- n06_commercial (nucleus that owns the crew instance)

## Escalation Protocol

If any role crosses its token ceiling or fails 3 consecutive quality
checks, emit `signal_{role}_escalate.json` to `.cex/runtime/signals/`. N07
reads and either extends budget (if justified) or terminates the crew with
partial results.

## Termination Criteria

ANY of:
1. `closer` signals `pipeline-complete` with quality >= 9.0
2. Token or wall-clock budget exhausted
3. `{{DEADLINE_ISO8601}}` passed
4. 3 consecutive quality rejects on the same artifact (stuck loop)

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p12_ct_sales_pipeline]] | parent |
| [[p02_ra_strategist]] | upstream |
| [[p02_ra_content_producer]] | upstream |
| [[p02_ra_closer]] | upstream |
