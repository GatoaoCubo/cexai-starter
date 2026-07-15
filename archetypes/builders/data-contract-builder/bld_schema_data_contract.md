---
quality: null
quality: null
id: bld_schema_data_contract
kind: input_schema
pillar: P06
llm_function: CONSTRAIN
version: 1.0.0
tags:
  - "input_schema"
  - "P06"
title: "Schema Data Contract"
author: builder
tldr: "Data Contract schema: data contract, field types, and validation rules"
8f: "F1_constrain"
keywords:
  - "schema data contract"
  - "data contract schema"
  - "data contract"
  - "field types"
  - "and validation rules"
  - "input_schema"
  - "## id pattern"
  - "frontmatter fields"
  - "body sections"
  - "versioning policy"
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_schema_usage_report
  - bld_schema_dataset_card
  - bld_schema_reranker_config
  - bld_schema_alert_rule
  - bld_schema_quickstart_guide
---
# Schema: data_contract
## Frontmatter Fields (Required)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string (dc_{prod}_{cons}_{entity}) | YES | snake_case |
| kind | literal "data_contract" | YES | — |
| pillar | literal "P06" | YES | — |
| title | string | YES | Human-readable contract name |
| version | semver | YES | Artifact version |
| quality | null | YES | Never self-score |
| producer_system | string | YES | System/team producing data |
| consumer_system | string | YES | System/team consuming data |
| entity | string | YES | Data entity name (PascalCase) |
| contract_version | semver | YES | Independent from impl version |
| effective_date | date YYYY-MM-DD | YES | When contract takes effect |
| tags | list[string] | YES | >= 3 tags |

## Body Sections (Required)
```markdown
## Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| {field} | {type} | {true/false} | {description} |

## SLA
| Metric | Threshold | Notes |
|--------|-----------|-------|
| freshness | {Xs / Xmin / 1h / daily} | Max age of data |
| availability | {99.X%} | Uptime guarantee |
| latency_p99 | {Xms} | 99th percentile response |

## Versioning Policy
- backward_compatible: {true/false}
- breaking_change_policy: {description}
- deprecation_notice: {X days}
```

## ID Pattern
`^dc_[a-z][a-z0-9_]+$`
Example: dc_sales_billing_order, dc_events_analytics_clickstream

## Constraints
- max_bytes: 4096
- schema section min 1 typed field
- SLA section min 1 numeric threshold
- contract_version independent from software version

## Schema Validation Checklist

- Verify all required fields have type annotations
- Validate enum values against domain vocabulary
- Cross-reference with related schemas for consistency
- Test schema parsing with sample data before publishing

## Schema Pattern

```yaml
# Schema validation contract
types_annotated: true
enums_valid: true
cross_refs_checked: true
sample_data_tested: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_schema_hydrate.py --check
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_usage_report | related | 0.50 |
| [[bld_schema_dataset_card]] | related | 0.50 |
| bld_schema_reranker_config | related | 0.48 |
| bld_schema_alert_rule | sibling | 0.47 |
| bld_schema_quickstart_guide | related | 0.47 |
