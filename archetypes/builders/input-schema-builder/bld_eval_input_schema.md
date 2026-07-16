---
kind: quality_gate
id: p11_qg_input_schema
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of input_schema artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Input Schema"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, input-schema, contract, fields, validation, coercion]
tldr: "Gates ensuring input_schema artifacts define complete, typed, unambiguous entry contracts with defaults, coercion rules, and at least one example."
domain: "input_schema — unilateral entry contracts defining required fields, types, and coercion rules"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [and coercion rules, input schema, coercion rules, quality-gate, input-schema, contract, fields]
density_score: 0.89
related:
  - bld_schema_input_schema
---
## Quality Gate

# Gate: Input Schema
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: input_schema` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error on any field |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | Uppercase, spaces, or leading digit |
| H03 | ID equals filename stem | `id: create_input` in file `edit_input.md` |
| H04 | Kind equals literal `input_schema` | Any other kind value |
| H05 | Quality field is `null` | Any non-null value |
| H06 | All required fields present | Missing: fields, required, version, or owner |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Type precision | 1.0 | Types use constrained vocabulary (string, integer, float, boolean, list, object, enum) | Types present but use freeform labels | Types missing or `any` used |
| S02 | Default coverage | 1.0 | All optional fields have explicit `default` values | Most optionals have defaults | No defaults on optional fields |
| S03 | Coercion rules | 1.0 | Fields that accept coercion list source types and target type explicitly | Coercion mentioned but unspecified | No coercion documentation |
| S04 | Constraint documentation | 1.0 | Fields with constraints (min, max, pattern, enum values) fully documented | Some constraints documented | Constraints implied but not stated |
| S05 | Error messages | 0.5 | Per-field error message or error code defined | Generic error messages only | No error documentation |
| S06 | Examples | 1.0 | At least 2 complete examples (one valid, one invalid input) | One example present | No examples |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to pool as golden input contract |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|
| Conditions | Rapidly evolving API where field set is not yet stable; schema explicitly marked `draft` |
| Approver | Owner agent lead |
| Audit trail | `bypass_reason` + `draft: true` both required in frontmatter |
| Expiry | Draft status expires after 14 days; must reach H-gate compliance or be deprecated |

## Examples

# Examples: input-schema-builder
## Golden Example
INPUT: "Define o input schema para o brain_query — what precisa receber para searchr"
OUTPUT:
```yaml
id: p06_is_brain_query
kind: input_schema
pillar: P06
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
scope: "brain_query search operation"
fields:
  - name: "query"
    type: "string"
    required: true
    default: null
    description: "Natural language search query"
    error_message: "query is required — provide a search string"
  - name: "max_results"
    type: "integer"
    required: false
    default: 10
    description: "Maximum number of results to return"
    error_message: null
  - name: "filters"
    type: "object"
    required: false
    default: null
    description: "Optional filters: {pillar, kind, domain, min_quality}"
    error_message: null
coercion:
  - from: "string"
    to: "integer"
    rule: "Parse max_results from string if numeric"
examples:
  - {query: "agent for research", max_results: 5}
  - {query: "P06 validators", filters: {pillar: "P06", kind: "validator"}}
domain: "brain-search"
quality: 8.9
tags: [input-schema, brain-query, search, P10]
tldr: "Input contract for brain_query: requires query string, optional max_results and filters."
density_score: 0.90
```
## Contract Definition
brain_query receives search requests from any agent/agent_group. Callers provide a natural
language query string, optional result limit, and optional filters by pillar/kind/domain.
## Fields
| # | Name | Type | Required | Default | Description |
|---|------|------|----------|---------|-------------|
| 1 | query | string | YES | - | Natural language search query |
| 2 | max_results | integer | NO | 10 | Max results to return |
| 3 | filters | object | NO | null | Filter by pillar, kind, domain, min_quality |
## Coercion Rules
| From | To | Rule |
|------|----|------|
| string | integer | Parse max_results from string if numeric |
## Examples
```json
{"query": "agent for research", "max_results": 5}
```
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p06_is_ pattern (H02 pass)
- kind: input_schema (H04 pass)
- 13+ required fields present (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
