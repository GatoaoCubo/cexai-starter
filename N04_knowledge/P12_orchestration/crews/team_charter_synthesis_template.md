---
id: team_charter_synthesis_template.md
kind: team_charter
8f: F8_collaborate
pillar: P12
llm_function: GOVERN
charter_id: "synthesis_{{instance_date}}"
crew_template_ref: p12_ct_knowledge_synthesis.md
mission_statement: "Synthesize {{domain_scope}} into structured, indexed knowledge_cards that fill identified library gaps and pass the P01 quality gate."
quality_gate: 9.0
deadline: "{{deadline_iso8601}}"
deliverables:
  - "raw_source_log (knowledge_card P01) -- source trail for all scanned material"
  - "gap_map (>=5 knowledge gaps identified and prioritized)"
  - ">=3 knowledge_cards (P01) curated, deduplicated, vocabulary-compliant"
  - "coverage_report (gap_resolution_rate >= 0.90, index entry count, broken-link count)"
budget:
  tokens: "{{budget_tokens}}"
  wall_clock_seconds: "{{budget_wall_clock_seconds}}"
  usd: "{{budget_usd}}"
stakeholders:
  - "{{orchestrator_id}}"
  - "n04_knowledge"
  - "{{consumer_nucleus}}"
escalation_protocol: "If any role crosses its token ceiling or fails 3 consecutive quality checks, emit signal_{role}_escalate.json to .cex/runtime/signals/. {{orchestrator_id}} reads and either extends budget or kills the crew."
termination_criteria: "ANY of: (1) indexer signals coverage_complete with gap_resolution_rate >= 0.90; (2) budget exhausted; (3) deadline passed; (4) 3 consecutive QA rejects on the same KC."
quality: null
keywords: [knowledge synthesis governance, team_charter, knowledge_synthesis, knowledge, template, domain_scope]
density_score: null
title: "Team Charter TEMPLATE -- Knowledge Synthesis"
version: "1.0.0"
tags: [team_charter, knowledge_synthesis, knowledge, template, n04]
tldr: "TEMPLATE -- instantiate by filling every {{open_var}}. Default mission contract for the knowledge_synthesis crew: source scan -> KC curation -> retrieval indexing in 3 sequential roles."
domain: "knowledge synthesis governance"
created: "2026-07-20"
slots:
  domain_scope: "<the knowledge area this crew instance targets>"
  budget_ceiling: "<token/time/usd caps for this instance -- defaults shown are starting points>"
related:
  - p12_ct_knowledge_synthesis.md
  - p02_ra_researcher.md
  - p02_ra_curator.md
  - p02_ra_indexer.md
  - team-charter-builder
  - cost-budget-builder
  - bld_collaboration_cost_budget
---

## How to instantiate this template

This file is a TEMPLATE, not an instance -- do not run it as-is. Copy it,
fill every `{{open_var}}`, drop the word "template" from the new
`charter_id` and filename (e.g. `team_charter_synthesis_launch01.md`),
then run:

```bash
python _tools/cex_crew.py run knowledge_synthesis \
    --charter N04_knowledge/P12_orchestration/crews/team_charter_synthesis_<instance>.md \
    --execute
```

## Mission Statement
Synthesize `{{domain_scope}}` into structured, indexed knowledge_cards that
fill identified library gaps and pass the P01 quality gate (>= 9.0 by
default, overridable via `quality_gate`). The output makes the domain
queryable via TF-IDF and wikilink traversal from any nucleus.

## Deliverables
1. raw_source_log (knowledge_card under P01) -- source trail for all scanned material
2. gap_map -- list of >=5 knowledge concepts missing or weak in the P01 library
3. >=3 knowledge_cards (P01) curated, deduplicated, vocabulary-compliant
4. coverage_report -- gap_resolution_rate, total_kcs_added, index_entry_count, broken_link_count

## Success Metrics
- Each knowledge_card quality >= `quality_gate` (default 9.0)
- gap_resolution_rate >= 0.90 (indexer-verified)
- Wall-clock under `{{budget_wall_clock_seconds}}`
- Token budget under `{{budget_tokens}}`
- All 3 a2a-task handoff signals present and parseable

## Budget
- Tokens: `{{budget_tokens}}` (hard ceiling; suggested split -- researcher 25%, curator 45%, indexer 30%)
- Wall-clock: `{{budget_wall_clock_seconds}}`
- USD: `{{budget_usd}}` at the nucleus's configured model pricing

## Stakeholders
- `{{orchestrator_id}}` (dispatches + monitors + consolidates)
- `n04_knowledge` (nucleus that owns the crew instance)
- `{{consumer_nucleus}}` (consumer of the synthesized knowledge_cards)

## Escalation Protocol
If any role crosses its token ceiling or fails 3 consecutive quality checks,
emit `signal_{role}_escalate.json` to `.cex/runtime/signals/`.
`{{orchestrator_id}}` reads and either extends budget (with justification) or
halts the crew cleanly.

## Termination Criteria
ANY of:
1. indexer signals `coverage_complete` with gap_resolution_rate >= 0.90
2. Token or wall-clock budget exhausted (crew halts; partial KCs committed)
3. Deadline (`{{deadline_iso8601}}`) passed
4. 3 consecutive QA rejects on the same KC (stuck curation loop)

## Domain Scope (fill in per instance)
```bash
python _tools/cex_crew.py run knowledge_synthesis \
    --charter N04_knowledge/P12_orchestration/crews/team_charter_synthesis_template.md \
    --var domain_scope="{{domain_scope}}" \
    --execute
```
There is no default scope -- `{{domain_scope}}` must be set before this
charter is instantiated.

### How to use

```text
You are the consuming agent that acts on this team_charter under F8 COLLABORATE.
- Resolve the open slots (domain_scope, budget_ceiling) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this team_charter defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F8 COLLABORATE.
2. Bind domain_scope and budget_ceiling from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the team_charter behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_knowledge_synthesis.md]] | related | 0.50 |
| [[p02_ra_researcher.md]] | upstream | 0.42 |
| [[p02_ra_curator.md]] | upstream | 0.41 |
| [[p02_ra_indexer.md]] | upstream | 0.38 |
| [[team-charter-builder]] | related | 0.25 |
| [[cost-budget-builder]] | related | 0.19 |
| [[bld_collaboration_cost_budget]] | related | 0.18 |
