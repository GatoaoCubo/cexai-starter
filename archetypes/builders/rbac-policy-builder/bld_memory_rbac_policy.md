---
kind: memory
id: p10_mem_rbac_policy_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for rbac_policy construction
quality: null
title: "Memory Rbac Policy"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [rbac_policy, builder, memory]
tldr: "Learned patterns and pitfalls for rbac_policy construction"
domain: "rbac_policy construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [rbac_policy construction, memory rbac policy, rbac_policy, builder, memory, observation
misaligned, pattern
granular, evidence
reviewed, related artifacts, resource scopes]
density_score: 0.85
related:
  - rbac-policy-builder
  - kc_rbac_policy
---
## Observation
Misaligned role hierarchies often cause unintended access overlaps, while overly broad resource scopes break tenant isolation. Policies frequently omit explicit tenant identifiers, leading to cross-tenant data exposure.

## Pattern
Granular role definitions paired with tenant-specific resource constraints ensure isolation. Hierarchical roles with inherited permissions reduce redundancy while maintaining clarity.

## Evidence
Reviewed policies using "tenant-abc-admin" roles with restricted resource paths demonstrated effective isolation. Overlapping roles in another artifact caused unauthorized access across tenants.

## Recommendations
- Enforce tenant-specific role names and resource scopes.
- Avoid wildcard resource patterns; use explicit path matching.
- Validate role inheritance to prevent accidental privilege escalation.
- Include tenant ID attributes in policy conditions for dynamic isolation.
- Audit policies for unused roles and redundant permissions quarterly.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[rbac-policy-builder]] | upstream | 0.55 |
| [[bld_knowledge_rbac_policy]] | upstream | 0.50 |
| [[kc_rbac_policy]] | upstream | 0.50 |
| [[bld_prompt_rbac_policy]] | upstream | 0.49 |
