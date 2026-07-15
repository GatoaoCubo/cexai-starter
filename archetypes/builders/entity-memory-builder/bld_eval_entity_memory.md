---
kind: quality_gate
id: p11_qg_entity_memory
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of entity_memory artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: entity_memory"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, entity-memory, P10, memory, entity, attributes]
tldr: "Pass/fail gate for entity_memory artifacts: entity_type validity, non-empty attributes, update_policy, confidence scoring, and relationship integrity."
domain: "entity memory — structured facts about named entities (people, tools, concepts, organizations, projects, services)"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [entity memory, entity_type validity, non-empty attributes, confidence scoring, and relationship integrity, quality-gate, entity-memory]
density_score: 0.90
related:
  - entity-memory-builder
  - bld_instruction_entity_memory
  - p11_qg_quality_gate
  - p11_qg_enum_def
  - bld_schema_entity_memory
---
## Quality Gate

# Gate: entity_memory
## Definition
| Field | Value |
|---|---|
| metric | entity_memory artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: entity_memory` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p10_em_[a-z][a-z0-9_]+$` | ID has hyphens, uppercase, or missing prefix |
| H03 | ID equals filename stem | `id: p10_em_stripe` but file is `p10_entity_stripe.md` |
| H04 | Kind equals literal `entity_memory` | `kind: memory` or `kind: learning_record` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `entity_type`, `attributes`, `name`, `tldr` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Attribute completeness | 1.0 | >= 3 meaningful attributes covering entity identity, status, and provenance |
| Attribute value quality | 1.0 | Values are specific facts, not vague descriptions; dates formatted YYYY-MM-DD |
| Entity type precision | 1.0 | entity_type matches actual nature of entity; not "concept" for a concrete tool |
| Relationship mapping | 1.0 | relationships field present with at least 1 link; relation type is a meaningful verb |
| Confidence scoring | 0.5 | confidence float present and in 0.0-1.0 range with plausible value |
| Update policy | 1.0 | update_policy declared and apownte for entity volatility |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Stub entity record used as placeholder during active research; not yet published |
| approver | Author self-certification with comment noting stub status |
| audit_trail | Bypass note in frontmatter comment with resolution date |
| expiry | 7d — stubs must be promoted to >= 7.0 or removed |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H10 (wrong kind corrupts memory index) |

## Examples

# Examples: entity-memory-builder
## Golden Example
INPUT: "Create entity memory for Firecrawl — the web scraping API service used by research_agent agent_group"
OUTPUT:
```yaml
id: p10_em_firecrawl
kind: entity_memory
pillar: P10
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "Firecrawl"
```
## Overview
Firecrawl is a web scraping service used by research_agent to enrich product research with live marketplace data. Tracks pricing, credits, API details, and integration status.
## Attributes
| Key | Value | Source |
|-----|-------|--------|
| provider | Mendable / Firecrawl Inc | official site |
| pricing_tier | $19/mo | pricing page |
| monthly_credits | 3000 | MEMORY.md |
| api_endpoint | https://api.firecrawl.dev/v1 | docs |
| integration_status | active | MEMORY.md |
## Relationships
| Entity | Relation | Notes |
|--------|----------|-------|
| p10_em_shaka_agent_group | used_by | research_agent uses Firecrawl for research |
| p10_em_organization_core | integrated_into | API key stored in Railway env |
## Update Policy
Policy: overwrite — pricing and credit values change with plan changes.
Conflict: latest confirmed value wins; set confidence 0.9 only if from official source.
Staleness: re-verify pricing tier at expiry 2027-01-01.

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches `^p10_em_` pattern (H02 pass)
- kind: entity_memory (H04 pass)
- entity_type: service (H08 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
