---
id: team_charter_build_review_template
kind: team_charter
pillar: P12
8f: F8_collaborate
llm_function: GOVERN
charter_id: "{{charter_id}}"
crew_template_ref: p12_ct_build_review
mission_statement: "{{mission_statement}}"
quality_gate: "{{quality_gate}}"
deadline: "{{deadline}}"
deliverables:
  - "{{deliverable_1}}"
  - "{{deliverable_2}}"
  - "{{deliverable_3}}"
budget:
  tokens: "{{budget_tokens}}"
  wall_clock_seconds: "{{budget_wall_clock_seconds}}"
  usd: "{{budget_usd}}"
spec_ref: "{{spec_ref}}"
stakeholders: ["{{stakeholder_1}}", "{{stakeholder_2}}"]
escalation_protocol: "{{escalation_protocol}}"
termination_criteria: "{{termination_criteria}}"
quality: null
title: "Team Charter Template -- Build-Review-Integrate"
version: "1.0.0"
tags: [team_charter, build_review, engineering, template]
tldr: "Fill-in-the-blanks mission contract for the build_review crew. Every {{open_var}} below must be bound at instantiation; the structure (deliverables, gates, termination) is fixed."
domain: "engineering build-review crew governance"
created: "2026-07-20"
keywords: [spec_ref, quality_gate, budget, escalation, termination, open_vars, crew_template_ref]
density_score: 0.85
related:
  - p12_ct_build_review
---

## How to use this template

```text
This file is a TEMPLATE, not a ready-to-run charter. Copy it, rename it
(e.g. team_charter_build_review_{{your_mission_slug}}.md), and replace every
{{open_var}} below with a concrete value before instantiation. The frontmatter
above and the body below must stay in sync -- if you change quality_gate in
one place, change it in both.
```

## Open Variables (fill before use)

| Variable | Type | Example | Notes |
|----------|------|---------|-------|
| `{{charter_id}}` | string | `build_review_20260901` | Unique per instantiation; convention: `{crew_name}_{YYYYMMDD}` |
| `{{mission_statement}}` | string | "Build and ship one hardened api_client spec from the integration notes in spec_ref" | One sentence: what gets built, from what source |
| `{{quality_gate}}` | float | `9.0` | The reviewer's accept bar; must be >= this project's 8.0 floor |
| `{{deadline}}` | ISO-8601 or null | `2026-09-05T18:00:00Z` | Hard cutoff; null means no deadline |
| `{{deliverable_1..3}}` | string | "Produced artifact (kind + pillar, compiled, quality >= gate)" | 1-3 concrete outputs; see Deliverables below for the default shape |
| `{{budget_tokens}}` | integer | `60000` | Hard ceiling across all 3 roles |
| `{{budget_wall_clock_seconds}}` | integer | `1800` | 30 minutes is a reasonable default for a single artifact |
| `{{budget_usd}}` | float | `2.50` | Estimate at your model's pricing |
| `{{spec_ref}}` | path | `N03_engineering/P01_knowledge/your_spec.md` | What the builder reads to know what to build |
| `{{stakeholder_1,2}}` | string | `"you"`, `"the_team"` | Who is Responsible/Accountable/Consulted/Informed |
| `{{escalation_protocol}}` | string | see Escalation Protocol below | What happens when a role gets stuck |
| `{{termination_criteria}}` | string | see Termination Criteria below | When the crew run stops, pass or fail |

## Mission Statement

`{{mission_statement}}`

Override `spec_ref` at instantiation; all other fields below are
production-ready defaults you may keep as-is.

## Deliverables

1. Produced artifact -- kind + pillar per `spec_ref`, compiled, `quality >= {{quality_gate}}`
2. Review report -- reviewer's score + per-gate evidence + pass/fail verdict
3. Consistency report -- integrator's cross-reference map + doctor status

## Success Metrics

- Builder's artifact has `quality: null` at hand-off (never self-scored)
- Reviewer's score is set independently and meets `{{quality_gate}}`
- Doctor check exits clean on the final artifact (integrator-verified)
- All 3 a2a-task handoff signals present in `.cex/runtime/signals/`
- Consistency report written before the crew-complete signal

## Budget

- Tokens: `{{budget_tokens}}` (hard ceiling; a reasonable default split is ~40% builder, ~30% reviewer, ~30% integrator)
- Wall-clock: `{{budget_wall_clock_seconds}}`
- USD: `{{budget_usd}}`

## Stakeholders

- `{{stakeholder_1}}` -- dispatches and monitors the crew
- `{{stakeholder_2}}` -- owns the produced artifact once shipped

RACI (Responsible/Accountable/Consulted/Informed):

| Stakeholder | Responsibility |
|-------------|-----------------|
| `{{stakeholder_1}}` | **A** -- accountable for the mission outcome |
| builder role | **R** -- production |
| reviewer role | **R** -- quality gate (independent scorer) |
| integrator role | **R** -- consistency + sign-off |

## Quality Gate

- **Target**: `quality_gate: {{quality_gate}}` -- the reviewer's accept bar
- **Floor**: this project's own hard floor (never publish below it, regardless of `{{quality_gate}}`)
- **Retry**: FAIL -> back to builder, max 2 retries per the reviewer's role_assignment
- **Enforcement**: the reviewer role is bound to a read-only agent -- it cannot "fix and pass" an artifact, only score and reject it

## Escalation Protocol

`{{escalation_protocol}}`

Default shape: if any role crosses its share of `{{budget_tokens}}` or fails
2 consecutive quality retries, emit `signal_{role}_escalate.json` to
`.cex/runtime/signals/`. The stakeholder holding this charter reads it and
chooses: extend budget, skip the artifact, or abort the crew with partial results.

## Termination Criteria

`{{termination_criteria}}`

Default shape -- ANY of:
1. integrator emits crew-complete signal with `doctor_status: pass`
2. Token budget (`{{budget_tokens}}`) exhausted
3. Wall-clock (`{{budget_wall_clock_seconds}}`) exceeded
4. 3 consecutive doctor failures on the same artifact (stuck loop)

## Instantiation

```bash
# 1. Copy this file and fill every {{open_var}} above.
# 2. Run:
python _tools/cex_crew.py run build_review \
    --charter N03_engineering/P12_orchestration/team_charter_build_review_{{your_mission_slug}}.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_build_review]] | related | 0.44 |
