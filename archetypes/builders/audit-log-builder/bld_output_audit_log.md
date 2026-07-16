---
kind: output_template
id: bld_output_template_audit_log
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for audit_log production
quality: null
title: "Output Template Audit Log"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [audit_log, builder, output_template]
tldr: "Output template for audit log: frontmatter field guide, required body sections, filled example, and quality gate checklist for immutable audit log configuration for soc2 type ii compliance."
domain: "audit_log construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [audit_log construction, output template audit log, frontmatter field guide, required body sections, filled example, type ii compliance, audit_log, builder, output_template, quality gate checklist]
density_score: 0.85
related:
  - bld_output_template_collaboration_pattern
  - bld_output_template_visual_workflow
  - bld_output_template_dataset_card
  - bld_output_template_thinking_config
  - bld_config_audit_log
---
```yaml
---
id: p11_al_{{name}}.md
name: {{audit_log_name}}
description: <!-- Brief description of the audit log purpose -->
version: {{version}}
quality: null
log_type: {{log_type}}
retention_period: {{retention_days}}
sample_data:
  - timestamp: <!-- ISO 8601 date/time -->
    user: <!-- User ID or system name -->
    action: <!-- Action performed -->
    status: <!-- Success/failure indicator -->
```

| Timestamp       | User    | Action        | Status  |
|-----------------|---------|---------------|---------|
| 2023-10-01T08:00 | user123 | login         | success |
| 2023-10-01T08:05 | admin   | config_change | success |

```json
{
  "event_id": "p11_al_{{event_id}}",
  "details": {
    "resource": "{{resource_name}}",
    "operation": "{{operation_type}}"
  }
}
```

## Quality Gate Checklist

| Gate | Check | Pass Condition |
|------|-------|---------------|
| H01 | Frontmatter complete | All required fields present with valid types |
| H02 | ID matches filename | id field equals filename stem |
| H03 | Naming convention | Follows p11_al_{{name}}.yaml pattern |
| H04 | Body sections present | All required sections non-empty |
| H05 | Size within limits | Total <= 3072 bytes |
| H06 | No placeholder text | No `{{var}}` unreplaced |
| H07 | quality: null | Never self-scored |

## Properties

| Property | Value |
|----------|-------|
| Kind | `output` |
| Pillar | P05 |
| Domain | audit log construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_collaboration_pattern]] | sibling | 0.36 |
| [[bld_output_template_visual_workflow]] | sibling | 0.34 |
| [[bld_output_template_dataset_card]] | sibling | 0.33 |
| [[bld_output_template_thinking_config]] | sibling | 0.30 |
| [[bld_config_audit_log]] | downstream | 0.30 |
