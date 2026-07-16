---
id: bld_output_data_contract
kind: output_template
pillar: P05
llm_function: PRODUCE
version: 1.0.0
quality: null
tags: [data_contract, template, output]
title: "Output Template: data_contract"
author: builder
tldr: "Data Contract prompt: output template, formatting rules, and structure"
8f: "F6_produce"
keywords: [output template, data contract prompt, formatting rules, and structure, data_contract, template, output, data contract, measurement method, versioning policy]
density_score: 1.0
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_schema_data_contract
  - data-contract-builder
---
# Output Template: data_contract
```markdown
---
id: dc_{{producer_snake}}_{{consumer_snake}}_{{entity_snake}}
kind: data_contract
pillar: P06
title: "{{Producer}} -> {{Consumer}}: {{Entity}} Contract"
version: 1.0.0
quality: null
producer_system: {{producer_system}}
consumer_system: {{consumer_system}}
entity: {{EntityPascalCase}}
contract_version: 1.0.0
effective_date: "{{YYYY-MM-DD}}"
tags: [{{producer}}, {{consumer}}, data-contract]
---

# {{Producer}} -> {{Consumer}}: {{Entity}} Data Contract

## Overview
{{One sentence describing what data the producer exposes to the consumer.}}

## Schema
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| {{field_1}} | {{type}} | {{true/false}} | {{description}} |
| {{field_2}} | {{type}} | {{true/false}} | {{description}} |

## SLA
| Metric | Threshold | Measurement Method |
|--------|-----------|-------------------|
| freshness | {{Xs/Xmin/Xh}} | {{how measured}} |
| availability | {{XX.X%}} | {{monitoring source}} |
| latency_p99 | {{Xms}} | {{percentile source}} |

## Versioning Policy
- backward_compatible: {{true/false}}
- breaking_change_policy: {{X days notice + migration guide}}
- deprecation_notice: {{X days}}

## Enforcement
- Schema registry: {{registry_url or "none"}}
- Contract tests: {{tool or "none"}}
- Owner: {{team_or_person}}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_data_contract]] | downstream | 0.39 |
| [[bld_prompt_data_contract]] | related | 0.37 |
| [[kc_data_contract]] | upstream | 0.36 |
| [[data-contract-builder]] | downstream | 0.35 |
