---
kind: output_template
id: bld_output_template_context_map
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a context_map artifact
pattern: every field here exists in SCHEMA.md -- template derives, never invents
quality: null
title: "Output Template Context Map"
version: "1.0.0"
author: n03_builder
tags: [context_map, builder, output_template]
tldr: "Fill-in template for context_map: BC inventory, relationships with DDD patterns, integration details, team coupling."
domain: "context map construction"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F6_produce"
keywords: [template with, context map construction, output template context map, fill-in template for context_map, bc inventory, relationships with ddd patterns, integration details, team coupling, context_map, builder]
density_score: 0.90
related:
  - bld_schema_context_map
  - context-map-builder
---
# Output Template: context_map

```yaml
id: p08_cm_{{system_slug}}
kind: context_map
pillar: P08
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
system_name: "{{human_friendly_system_name}}"
contexts_count: {{integer_count_of_BCs}}
quality: null
tags: [context_map, {{system_slug}}, {{domain_tag}}]
tldr: "{{dense_summary_max_160ch}}"
```

## Bounded Contexts

| Context | Team | Core Domain? | Description |
|---------|------|-------------|-------------|
| `{{ContextName1}}` | `{{TeamName1}}` | {{YES|SUPPORTING|GENERIC}} | `{{one_line_description}}` |
| `{{ContextName2}}` | `{{TeamName2}}` | {{YES|SUPPORTING|GENERIC}} | `{{one_line_description}}` |

## Relationships

| Upstream (U) | Downstream (D) | Pattern | Integration Type | Notes |
|-------------|----------------|---------|-----------------|-------|
| `{{ContextA}}` | `{{ContextB}}` | {{ACL|OHS|Conformist|Partnership|Shared_Kernel|Customer_Supplier}} | {{sync|async|batch}} | `{{brief_note}}` |

## Integration Details

| Relationship | Translation Layer | Protocol | Sync/Async |
|-------------|-----------------|----------|-----------|
| `{{ContextA}}` -> `{{ContextB}}` `{{Pattern}}` | `{{layer_name_or_none}}` | {{REST|Kafka|gRPC|EventBus}} | {{sync|async}} |

## Team Coupling

| Relationship | Coupling Level | Risk | Mitigation |
|-------------|----------------|------|-----------|
| `{{ContextA}}` -> `{{ContextB}}` (`{{Pattern}}`) | {{Low|Medium|High|Very High}} | `{{risk_description}}` | `{{mitigation_strategy}}` |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_context_map]] | downstream | 0.40 |
| [[context-map-builder]] | downstream | 0.33 |
