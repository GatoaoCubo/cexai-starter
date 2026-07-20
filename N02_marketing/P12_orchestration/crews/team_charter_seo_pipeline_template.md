---
id: team_charter_seo_pipeline_template.md
kind: team_charter
8f: F8_collaborate
pillar: P12
llm_function: GOVERN
charter_id: "{{CHARTER_ID | default: 'seo_pipeline_TEMPLATE'}}"
crew_template_ref: p12_ct_seo_pipeline.md
mission_statement: "Optimize '{{CONTENT_TARGET}}' for search around primary keyword {{PRIMARY_KEYWORD}}, publishing to {{PLATFORM | default: 'the blog'}}."
quality_gate: 8.5
deadline: "{{DEADLINE_ISO}}"
deliverables:
  - "Keyword brief (>= 5 target keywords with volume + difficulty + intent)"
  - "Optimized content (title, meta description, headings, body, internal links)"
  - "SEO score card (8 dimensions, composite + pass/fail gate)"
budget:
  tokens: "{{TOKEN_BUDGET | default: 80000}}"
  wall_clock_seconds: "{{WALL_CLOCK_BUDGET_SECONDS | default: 1440}}"
  usd: "{{USD_BUDGET | default: 3.50}}"
stakeholders: ["{{BRAND_NAME}}", "{{ORCHESTRATOR_ID}}", "{{OWNING_NUCLEUS | default: 'n02_marketing'}}"]
escalation_protocol: "If any role crosses budget ceiling, escalate via signal; do NOT silently truncate."
termination_criteria: "ANY of: (1) seo_scorer signals publish-approved; (2) budget exhausted; (3) deadline passed; (4) 2 consecutive scorer rejects on same optimized_content."
quality: null
keywords: [knowledge_card, a2a-task, qa-attested, wall-clock, token budget, role-level ceilings, escalation protocol, publish-approved, artifact]
density_score: null
title: "Team Charter Template -- SEO Pipeline"
version: "1.0.0"
tags: [team_charter, seo_pipeline, template]
tldr: "Fill-in-the-blanks mission contract for a seo_pipeline crew instance. Copy this file per content piece, never edit the template in place."
domain: "seo pipeline governance"
created: "2026-07-20"
related:
  - p12_ct_seo_pipeline.md
  - p02_ra_seo_scorer.md
---

## How to Use This Template

1. Copy this file to a mission-specific name, e.g.
   `team_charter_seo_pipeline_<slug>.md`.
2. Fill every `{{open_var}}` -- do not run the crew against unfilled
   placeholders.
3. Pass the copy's path to `cex_crew.py run seo_pipeline --charter <path>`.

## Mission Statement
Optimize **{{CONTENT_TARGET}}** for search around primary keyword
**{{PRIMARY_KEYWORD}}**, publishing to **{{PLATFORM | default: 'the blog'}}**.

## Deliverables
1. Keyword brief (>= 5 target keywords with volume + difficulty + intent)
2. Optimized content (title, meta description, headings, body, internal links)
3. SEO score card (8 dimensions, composite + pass/fail gate)

## Success Metrics
- SEO score card composite >= `{{QUALITY_GATE | default: 8.5}}`
- Wall-clock under `{{WALL_CLOCK_BUDGET_SECONDS | default: 1440}}`s for the full crew
- Token budget under `{{TOKEN_BUDGET | default: 80000}}` total
- All 3 a2a-task handoff signals present
- Keyword density <= 2.5% per keyword (no stuffing)

## Budget
- Tokens: `{{TOKEN_BUDGET | default: 80000}}` (hard ceiling; role-level ceilings allocated 1/3 each)
- Wall-clock: `{{WALL_CLOCK_BUDGET_SECONDS | default: 1440}}`s
- USD: `{{USD_BUDGET | default: 3.50}}` at your default model's pricing

## Stakeholders
- `{{BRAND_NAME}}` (content owner -- decides WHAT)
- `{{ORCHESTRATOR_ID}}` (dispatches + monitors + consolidates)
- `{{OWNING_NUCLEUS | default: 'n02_marketing'}}` (nucleus that owns the crew instance)

## Escalation Protocol
If any role crosses its budget ceiling or fails 2 consecutive scorer rejects,
emit `signal_{role}_escalate.json` to `.cex/runtime/signals/`. The
orchestrator reads it and either extends budget (if justified) or kills the
crew.

## Termination Criteria
ANY of:
1. seo_scorer signals `publish-approved`
2. Token or wall-clock budget exhausted
3. Deadline passed (`{{DEADLINE_ISO}}`)
4. 2 consecutive scorer rejects on the same optimized_content (stuck loop)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_seo_pipeline.md]] | related | 0.40 |
| [[p02_ra_seo_scorer.md]] | upstream | 0.24 |
