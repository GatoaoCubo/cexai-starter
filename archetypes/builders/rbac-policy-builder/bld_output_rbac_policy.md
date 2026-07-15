---
kind: output_template
id: bld_output_template_rbac_policy
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for rbac_policy production
quality: null
title: "Output Template Rbac Policy"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [rbac_policy, builder, output_template]
tldr: "Output template for rbac policy: frontmatter field guide, required body sections, filled example, and quality gate checklist for role-based access control policy for multi-tenant isolation."
domain: "rbac_policy construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [rbac_policy construction, output template rbac policy, frontmatter field guide, required body sections, filled example, rbac_policy, builder, output_template, quality gate checklist, pass condition]
density_score: 0.85
related:
  - bld_output_template_dataset_card
  - bld_output_template_collaboration_pattern
  - bld_output_template_thinking_config
  - bld_output_template_visual_workflow
  - bld_output_query_optimizer
---
```yaml
---
id: p09_rbac_{{policy_name}}.yaml <!-- Use pattern: p09_rbac_[a-z][a-z0-9_]+.yaml -->
name: {{policy_name}} <!-- Human-readable policy name -->
kind: rbac_policy
pillar: P09
quality: null <!-- Must remain null -->
---
```

| Role       | Resource       | Actions          |
|------------|----------------|------------------|
| admin      | /v1/*          | ["*"]            |
| viewer     | /v1/data/*     | ["GET"]          |

```yaml
rules:
  - role: {{role_name}} <!-- e.g., "admin" or "viewer" -->
    resource: {{resource_path}} <!-- e.g., "/v1/data/*" -->
    actions: <!-- List of allowed actions -->
      - {{action}} <!-- e.g., "GET", "POST", "*" -->
```

## Quality Gate Checklist

| Gate | Check | Pass Condition |
|------|-------|---------------|
| H01 | Frontmatter complete | All required fields present with valid types |
| H02 | ID matches filename | id field equals filename stem |
| H03 | Naming convention | Follows p09_rbac_{{name}}.yaml pattern |
| H04 | Body sections present | All required sections non-empty |
| H05 | Size within limits | Total <= 4096 bytes |
| H06 | No placeholder text | No `{{var}}` unreplaced |
| H07 | quality: null | Never self-scored |

## Properties

| Property | Value |
|----------|-------|
| Kind | `output` |
| Pillar | P05 |
| Domain | rbac policy construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_dataset_card]] | sibling | 0.30 |
| bld_output_template_collaboration_pattern | sibling | 0.30 |
| bld_output_template_thinking_config | sibling | 0.29 |
| bld_output_template_visual_workflow | sibling | 0.28 |
| bld_output_query_optimizer | sibling | 0.27 |
