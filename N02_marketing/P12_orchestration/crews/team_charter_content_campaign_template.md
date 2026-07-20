---
id: team_charter_content_campaign_template.md
kind: team_charter
8f: F8_collaborate
pillar: P12
llm_function: GOVERN
charter_id: "{{CHARTER_ID | default: 'content_campaign_TEMPLATE'}}"
crew_template_ref: p12_ct_content_campaign.md
mission_statement: "Ship a {{CADENCE | default: 'monthly'}} multi-channel content campaign for '{{CAMPAIGN_NAME}}' targeting {{TARGET_AUDIENCE}} across {{CHANNELS | default: 'social, email, blog'}}."
quality_gate: 9.0
deadline: "{{DEADLINE_ISO}}"
deliverables:
  - "Strategy brief (knowledge_card P01) -- audience segments + channel mapping + messaging angles"
  - "Content template pack (>= 1 template per channel: social, email, blog)"
  - "Review report (brand voice + CTA + channel-fit scores, pass/fail)"
budget:
  tokens: "{{TOKEN_BUDGET | default: 90000}}"
  wall_clock_seconds: "{{WALL_CLOCK_BUDGET_SECONDS | default: 1500}}"
  usd: "{{USD_BUDGET | default: 4.00}}"
stakeholders: ["{{BRAND_NAME}}", "{{ORCHESTRATOR_ID}}", "{{OWNING_NUCLEUS | default: 'n02_marketing'}}"]
escalation_protocol: "If any role crosses budget ceiling, escalate via signal; do NOT silently truncate."
termination_criteria: "ANY of: (1) reviewer signals campaign-approved; (2) budget exhausted; (3) deadline passed; (4) 2 consecutive review rejects on same template_pack."
quality: null
keywords: [knowledge_card, a2a-task, qa-attested, wall-clock, token budget, role-level ceilings, escalation protocol, campaign-approved, artifact]
density_score: null
title: "Team Charter Template -- Content Campaign"
version: "1.0.0"
tags: [team_charter, content_campaign, template]
tldr: "Fill-in-the-blanks mission contract for a content_campaign crew instance. Copy this file per campaign, never edit the template in place."
domain: "content campaign governance"
created: "2026-07-20"
related:
  - p12_ct_content_campaign.md
  - p02_ra_content_reviewer.md
---

## How to Use This Template

1. Copy this file to a mission-specific name, e.g.
   `team_charter_content_campaign_<slug>.md`.
2. Fill every `{{open_var}}` -- do not run the crew against unfilled
   placeholders.
3. Pass the copy's path to `cex_crew.py run content_campaign --charter <path>`.

## Mission Statement
Ship a **{{CADENCE | default: 'monthly'}}** multi-channel content campaign for
**{{CAMPAIGN_NAME}}** targeting **{{TARGET_AUDIENCE}}** across
**{{CHANNELS | default: 'social, email, blog'}}**.

## Deliverables
1. Strategy brief (knowledge_card under P01) -- audience segments, channel mapping, messaging angles
2. Content template pack (>= 1 template per channel: social, email, blog)
3. Review report (brand voice + CTA + channel-fit scores, pass/fail)

## Success Metrics
- Each deliverable quality >= `{{QUALITY_GATE | default: 9.0}}` (reviewer-attested)
- Wall-clock under `{{WALL_CLOCK_BUDGET_SECONDS | default: 1500}}`s for the full crew
- Token budget under `{{TOKEN_BUDGET | default: 90000}}` total
- All 3 a2a-task handoff signals present

## Budget
- Tokens: `{{TOKEN_BUDGET | default: 90000}}` (hard ceiling; role-level ceilings allocated 1/3 each)
- Wall-clock: `{{WALL_CLOCK_BUDGET_SECONDS | default: 1500}}`s
- USD: `{{USD_BUDGET | default: 4.00}}` at your default model's pricing

## Stakeholders
- `{{BRAND_NAME}}` (campaign owner -- decides WHAT)
- `{{ORCHESTRATOR_ID}}` (dispatches + monitors + consolidates)
- `{{OWNING_NUCLEUS | default: 'n02_marketing'}}` (nucleus that owns the crew instance)

## Escalation Protocol
If any role crosses its budget ceiling or fails 2 consecutive review rejects,
emit `signal_{role}_escalate.json` to `.cex/runtime/signals/`. The
orchestrator reads it and either extends budget (if justified) or kills the
crew.

## Termination Criteria
ANY of:
1. reviewer signals `campaign-approved`
2. Token or wall-clock budget exhausted
3. Deadline passed (`{{DEADLINE_ISO}}`)
4. 2 consecutive review rejects on the same template_pack (stuck loop)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_content_campaign.md]] | related | 0.40 |
| [[p02_ra_content_reviewer.md]] | upstream | 0.24 |
