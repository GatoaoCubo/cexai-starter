---
id: team_charter_taxonomy_audit_template.md
kind: team_charter
8f: F8_collaborate
pillar: P12
llm_function: GOVERN
charter_id: "taxonomy_audit_{{instance_date}}"
crew_template_ref: p12_ct_taxonomy_audit.md
mission_statement: "Audit the kind taxonomy against {{taxonomy_scope}} industry vocabularies, close validated gaps, and promote only entries that clear the taxonomy_validator gate."
quality_gate: 9.0
deadline: "{{deadline_iso8601}}"
deliverables:
  - "gap_report.md (>=5 ranked, sourced taxonomy gaps)"
  - "glossary entries for every high+medium priority gap (term, definition, pillar, industry_source, disambiguation)"
  - "validation_report.md (PASS/FAIL/REVISE per entry + overall crew_pass boolean)"
budget:
  tokens: "{{budget_tokens}}"
  wall_clock_seconds: "{{budget_wall_clock_seconds}}"
  usd: "{{budget_usd}}"
stakeholders:
  - "{{orchestrator_id}}"
  - "n04_knowledge"
  - "{{consumer_nucleus}}"
escalation_protocol: "If any role crosses its budget ceiling or fails 3 consecutive quality checks, emit signal_{role}_escalate.json to .cex/runtime/signals/. {{orchestrator_id}} reads it and either extends budget or kills the crew."
termination_criteria: "ANY of: (1) taxonomy_validator signals crew_pass=true with FAIL rate <= 10%; (2) budget exhausted; (3) deadline passed; (4) 3 consecutive quality rejects on the same gap entry."
quality: null
title: "Team Charter TEMPLATE -- Taxonomy Audit"
version: "1.0.0"
tags: [team_charter, taxonomy_audit, knowledge, template, n04]
tldr: "TEMPLATE -- instantiate by filling every {{open_var}}. Default mission contract for the taxonomy_audit crew: gap scan -> definition writing -> taxonomy validation in 3 sequential roles."
domain: "taxonomy audit governance"
created: "2026-07-20"
slots:
  taxonomy_scope: "<which framework(s) or domain area to audit against -- e.g. a named agent framework, a protocol family, a vertical vocabulary>"
  budget_ceiling: "<token/time/usd caps for this instance -- defaults shown are starting points>"
related:
  - p12_ct_taxonomy_audit.md
  - p02_ra_gap_finder.md
  - p02_ra_definer.md
  - p02_ra_taxonomy_validator.md
  - team-charter-builder
---

## How to instantiate this template

This file is a TEMPLATE, not an instance -- do not run it as-is. Copy it,
fill every `{{open_var}}`, drop the word "template" from the new
`charter_id` and filename (e.g. `team_charter_taxonomy_audit_q3.md`), then
run:

```bash
python _tools/cex_crew.py run taxonomy_audit \
    --charter N04_knowledge/P12_orchestration/crews/team_charter_taxonomy_audit_<instance>.md \
    --execute
```

## Mission Statement

Audit the kind taxonomy against `{{taxonomy_scope}}` industry vocabularies,
close validated gaps with precise glossary entries, and promote only the
entries that clear the taxonomy_validator gate. Owner: N04 (knowledge).
Consumers: N03 (builder creation for any promoted kind), N05 (kinds_meta.json
updates).

## Deliverables

1. gap_report.md (P01, audit trail) -- >= 5 ranked, sourced taxonomy gaps
2. Glossary entries for every high+medium priority gap -- term, definition,
   pillar assignment, industry_source, disambiguation notes
3. validation_report.md (P07 archive) -- PASS/FAIL/REVISE per entry + overall
   `crew_pass` boolean

## Success Metrics

- gap_finder produces >= 5 validated gaps, each traced to a real industry concept
- definer produces entries for all high+medium priority gaps, quality >= `quality_gate`
- taxonomy_validator FAIL rate <= 10% of total entries before `crew_pass=true`
- Wall-clock under `{{budget_wall_clock_seconds}}` for the full crew
- Token budget under `{{budget_tokens}}` total
- All 3 a2a-task handoff signals present, in order, none below quality 8.0

## Budget

- Tokens: `{{budget_tokens}}` (hard ceiling; suggested split -- gap_finder 30%, definer 45%, taxonomy_validator 25%)
- Wall-clock: `{{budget_wall_clock_seconds}}` seconds
- USD: `{{budget_usd}}`

## Stakeholders

- `{{orchestrator_id}}` (dispatches + monitors + consolidates)
- n04_knowledge (nucleus that owns the crew instance)
- `{{consumer_nucleus}}` (consumer of promoted kinds -- typically the builder nucleus)

## Escalation Protocol

If any role crosses its budget ceiling or fails 3 consecutive quality checks,
emit `signal_{role}_escalate.json` to `.cex/runtime/signals/`.
`{{orchestrator_id}}` reads it and either extends the budget (if justified) or
terminates the crew with partial results.

## Termination Criteria

ANY of:
1. `taxonomy_validator` signals `crew_pass=true` with FAIL rate <= 10%
2. Token or wall-clock budget exhausted
3. `{{deadline_iso8601}}` passed
4. 3 consecutive quality rejects on the same gap entry (stuck loop)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_taxonomy_audit.md]] | parent | 0.50 |
| [[p02_ra_gap_finder.md]] | upstream | 0.36 |
| [[p02_ra_definer.md]] | upstream | 0.36 |
| [[p02_ra_taxonomy_validator.md]] | upstream | 0.36 |
| [[team-charter-builder]] | related | 0.22 |
