---
id: team_charter_knowledge_pipeline_template.md
kind: team_charter
8f: F8_collaborate
pillar: P12
llm_function: GOVERN
charter_id: "knowledge_pipeline_{{instance_date}}"
crew_template_ref: p12_ct_knowledge_pipeline.md
mission_statement: "Ingest {{domain_scope}} into structured, indexed knowledge_cards that fill identified library gaps and pass the P01 quality gate."
quality_gate: 9.0
deadline: "{{deadline_iso8601}}"
deliverables:
  - "raw_source_log (>=3 sources with trust_level + format)"
  - ">=3 knowledge_cards (P01) curated, deduplicated, vocabulary-compliant, versioned on overwrite"
  - "coverage_report (gap_resolution_rate >= 0.90, index entry count, broken-link count)"
budget:
  tokens: 60000
  wall_clock_seconds: 1500
  usd: 2.50
stakeholders:
  - "{{orchestrator_id}}"
  - "n04_knowledge"
  - "{{consumer_nucleus}}"
escalation_protocol: "If any role crosses its token ceiling or fails 3 consecutive quality checks, emit signal_{role}_escalate.json to .cex/runtime/signals/. {{orchestrator_id}} reads and either extends budget or halts the crew."
termination_criteria: "ANY of: (1) indexer signals coverage_complete with gap_resolution_rate >= 0.90; (2) budget exhausted; (3) deadline passed; (4) 3 consecutive QA rejects on the same knowledge_card."
quality: null
keywords: [knowledge pipeline governance, team_charter, knowledge_pipeline, versioning, template, domain_scope]
density_score: null
title: "Team Charter Template -- Knowledge Pipeline"
version: "1.0.0"
tags: [team_charter, knowledge_pipeline, template, P12]
tldr: "Fill-in-the-blanks mission contract for the knowledge_pipeline crew; instantiate per domain."
domain: "knowledge pipeline governance"
created: "2026-07-20"
slots:
  domain_scope: "<the knowledge area this crew instance targets>"
  budget_ceiling: "<token/time/usd caps for this instance -- defaults shown are starting points>"
related:
  - p12_ct_knowledge_pipeline.md
  - p02_ra_ingester.md
  - p02_ra_curator.md
  - p02_ra_indexer.md
  - team-charter-builder
---

## Mission Statement
Ingest `{{domain_scope}}` into structured, indexed knowledge_cards that fill
identified library gaps and pass the P01 quality gate (>= 9.0 by default,
overridable via `quality_gate`). The output makes the domain queryable via
the retrieval index and wikilink traversal from any nucleus.

## Deliverables
1. raw_source_log -- >=3 sources, each with trust_level + format
2. >=3 knowledge_cards (P01) curated, deduplicated, vocabulary-compliant
3. coverage_report -- gap_resolution_rate, total_kcs_added, index_entry_count, broken_link_count
4. Every version-bumped knowledge_card carries a superseded-fact link (never a silent overwrite)

## Success Metrics
- Each knowledge_card quality >= `quality_gate` (default 9.0)
- gap_resolution_rate >= 0.90 (indexer-verified)
- Wall-clock under `budget.wall_clock_seconds`
- Token budget under `budget.tokens`
- All 3 a2a-task handoff signals present and parseable
- Zero facts overwritten without a version trail

## Budget
- Tokens: `{{budget_tokens}}` (defaults shown above; suggested split -- ingester 25%, curator 45%, indexer 30%)
- Wall-clock: `{{budget_wall_clock_seconds}}`
- USD: `{{budget_usd}}` at the nucleus's configured model pricing

## Stakeholders
- `{{orchestrator_id}}` (dispatches + monitors + consolidates)
- `n04_knowledge` (nucleus that owns the crew instance)
- `{{consumer_nucleus}}` (consumer of the resulting knowledge_cards)

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
4. 3 consecutive QA rejects on the same knowledge_card (stuck curation loop)

## Domain Scope (fill in per instance)
```bash
python _tools/cex_crew.py run knowledge_pipeline \
    --charter N04_knowledge/P12_orchestration/team_charter_knowledge_pipeline_template.md \
    --var domain_scope="{{domain_scope}}" \
    --execute
```
There is no default scope -- `{{domain_scope}}` must be set before this
charter is instantiated; the crew_template will not run against an
unresolved placeholder.

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
| [[p12_ct_knowledge_pipeline.md]] | related | 0.50 |
| [[p02_ra_ingester.md]] | upstream | 0.38 |
| [[p02_ra_curator.md]] | upstream | 0.40 |
| [[p02_ra_indexer.md]] | upstream | 0.36 |
| [[team-charter-builder]] | related | 0.25 |
