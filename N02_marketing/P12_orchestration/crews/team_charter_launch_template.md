---
id: team_charter_launch_template
kind: team_charter
8f: F8_collaborate
pillar: P12
llm_function: GOVERN
charter_id: "{{CHARTER_ID | default: 'launch_TEMPLATE'}}"
crew_template_ref: p12_ct_product_launch.md
mission_statement: "Ship a launch package for '{{PRODUCT_NAME}}' targeting {{TARGET_AUDIENCE}}."
quality_gate: 9.0
deadline: "{{DEADLINE_ISO}}"
deliverables:
  - "Positioning brief (knowledge_card P01) -- source of truth for copy + design"
  - "Launch copy pack (tagline + headline + 3 body variants)"
  - "Visual assets spec (hero + social + email header)"
  - "Final verdict report (quality scores + pass/fail)"
budget:
  tokens: "{{TOKEN_BUDGET | default: 120000}}"
  wall_clock_seconds: "{{WALL_CLOCK_BUDGET_SECONDS | default: 1800}}"
  usd: "{{USD_BUDGET | default: 5.00}}"
stakeholders: ["{{BRAND_NAME}}", "{{ORCHESTRATOR_ID}}", "{{OWNING_NUCLEUS | default: 'n02_marketing'}}"]
escalation_protocol: "If any role crosses budget ceiling, escalate via signal; do NOT silently truncate."
termination_criteria: "ANY of: (1) qa_reviewer signals launch-approved; (2) budget exhausted; (3) deadline passed; (4) 3 consecutive QA rejects on same artifact."
quality: null
keywords: [knowledge_card, a2a-task, qa-attested, wall-clock, token budget, role-level ceilings, escalation protocol, launch-approved, artifact]
density_score: 0.95
title: "Team Charter Template -- Product Launch"
version: "1.0.0"
tags: [team_charter, product_launch, template]
tldr: "Fill-in-the-blanks mission contract for a product_launch crew instance. Copy this file per launch, never edit the template in place."
domain: "product launch governance"
created: "2026-07-20"
related:
  - p12_ct_product_launch.md
  - p02_ra_qa_reviewer.md
---

## How to Use This Template

1. Copy this file to a mission-specific name, e.g.
   `team_charter_launch_<slug>.md`.
2. Fill every `{{open_var}}` -- do not run the crew against unfilled
   placeholders.
3. Pass the copy's path to `cex_crew.py run product_launch --charter <path>`.

## Mission Statement
Ship a launch package for **{{PRODUCT_NAME}}** targeting **{{TARGET_AUDIENCE}}**.

## Deliverables
1. Positioning brief (knowledge_card under P01) -- source of truth for copy and design
2. Launch copy pack (tagline + headline + 3 body variants)
3. Visual assets spec (hero + social + email header)
4. Final verdict report (quality scores + pass/fail)

## Success Metrics
- Each deliverable quality >= `{{QUALITY_GATE | default: 9.0}}` (QA-attested)
- Wall-clock under `{{WALL_CLOCK_BUDGET_SECONDS | default: 1800}}`s for the full crew
- Token budget under `{{TOKEN_BUDGET | default: 120000}}` total
- All 4 a2a-task handoff signals present

## Budget
- Tokens: `{{TOKEN_BUDGET | default: 120000}}` (hard ceiling; role-level ceilings allocated 1/4 each)
- Wall-clock: `{{WALL_CLOCK_BUDGET_SECONDS | default: 1800}}`s
- USD: `{{USD_BUDGET | default: 5.00}}` at your default model's pricing

## Stakeholders
- `{{BRAND_NAME}}` (product owner -- decides WHAT)
- `{{ORCHESTRATOR_ID}}` (dispatches + monitors + consolidates)
- `{{OWNING_NUCLEUS | default: 'n02_marketing'}}` (nucleus that owns the crew instance)

## Escalation Protocol
If any role crosses its budget ceiling or fails 3 consecutive QA rejects,
emit `signal_{role}_escalate.json` to `.cex/runtime/signals/`. The
orchestrator reads it and either extends budget (if justified) or kills the
crew.

## Termination Criteria
ANY of:
1. qa_reviewer signals `launch-approved`
2. Token or wall-clock budget exhausted
3. Deadline passed (`{{DEADLINE_ISO}}`)
4. 3 consecutive QA rejects on the same artifact (stuck loop)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_product_launch.md]] | related | 0.40 |
| [[p02_ra_qa_reviewer.md]] | upstream | 0.24 |
