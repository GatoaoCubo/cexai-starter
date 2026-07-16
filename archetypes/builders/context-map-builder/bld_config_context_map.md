---
quality: null
quality: null
kind: config
id: bld_config_context_map
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
title: "Config Context Map"
version: "1.0.0"
author: n03_builder
tags: [context_map, builder, config]
tldr: "Naming: p08_cm_{slug}.md. Contexts table + relationships table required. Team coupling documented."
domain: "context map construction"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, context map construction, config context map, contexts table, relationships table required, team coupling documented, context_map]
density_score: 0.90
related:
  - p10_lr_context_map_builder
  - kc_context_map
  - bld_knowledge_card_context_map
  - p11_qg_context_map
  - bld_instruction_context_map
---
# Config: context_map Production Rules

## Naming Convention

| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p08_cm_{system_slug}.md` | `p08_cm_ecommerce_platform.md` |
| Builder directory | kebab-case | `context-map-builder/` |
| Frontmatter fields | snake_case | `system_name`, `contexts_count` |
| System slug | snake_case, lowercase | `ecommerce_platform`, `saas_crm` |
| BC names | PascalCase | `Orders`, `Inventory`, `Payments` |
| Pattern values | PascalCase enum | `ACL`, `OHS`, `Conformist`, `Partnership` |

Rule: id MUST equal filename stem. Hyphens in id = HARD FAIL.

## File Paths

- Output: `N0X_{domain}/P08_architecture/p08_cm_{system_slug}.md`
- Compiled: `N0X_{domain}/P08_architecture/compiled/p08_cm_{system_slug}.yaml`

## Size Limits

- Body: max 4096 bytes
- Density: >= 0.80 (tables > prose)

## Pattern Selection Guide

| Situation | Pattern to Use |
|-----------|----------------|
| Legacy system integration (protect from model rot) | ACL |
| Stable API with formal versioning | OHS |
| Small startup, teams willing to share model | Conformist (temporary) |
| Two new teams building together | Partnership |
| Single shared codebase subset | Shared Kernel (HIGH risk) |
| One team has backlog control | Customer/Supplier |

## Team Coupling Risk Register

| Pattern | Coupling | Typical Team Risk |
|---------|----------|------------------|
| ACL | Low | Translation overhead only |
| OHS | Low | API versioning maintenance |
| Published Language | Low | Formal spec maintenance |
| Conformist | HIGH | Upstream changes break downstream |
| Customer/Supplier | Medium | Backlog dependency |
| Partnership | VERY HIGH | Joint releases required |
| Shared Kernel | VERY HIGH | Coordinated commits required |

## Integration Type Selection

| Coupling Scenario | Integration Type | Notes |
|------------------|-----------------|-------|
| Real-time request/response | sync | REST, gRPC |
| Event-driven notification | async | Kafka, EventBridge, SNS |
| Nightly data exchange | batch | ETL, data pipeline |
| Historical migration | batch | One-time or periodic |

## Review Cadence

| Event | Action |
|-------|--------|
| New service added | Add to contexts table; identify relationships |
| Team restructure | Update team_coupling and ownership |
| Conformist relationship | Quarterly review for ACL migration readiness |
| Quarterly review | Verify all patterns still accurate |

## BC Entry Required Fields

| Field | Format | Example |
|-------|--------|---------|
| bc_name | PascalCase | Orders, Inventory, Payments |
| owning_team | string | platform-team, commerce-team |
| language | brief description | "Order, LineItem, Fulfillment" |
| type | core / supporting / generic | core |

## Common Config Mistakes

| Mistake | Consequence | Correct Behavior |
|---------|-------------|-----------------|
| Unlabeled relationships | Map decays in months | Always label with DDD pattern |
| Missing team ownership | Nobody updates the map | Assign owning team per BC |
| Conformist without plan | Blocking dependency later | Flag with ACL migration path |
| Shared Kernel for all | Joint release trains | Use only when absolutely necessary |
| Missing integration_type | Fault isolation gap | Declare sync/async/batch for each relationship |
| relationships_count | integer | Count of BC relationship rows |
| Relationship table missing integration_type | Sync vs async gap | Always declare integration_type per relationship |
| BC missing owning_team | Governance gap | Assign owning team to every BC |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_lr_context_map_builder]] | downstream | 0.52 |
| [[kc_context_map]] | upstream | 0.46 |
| [[bld_knowledge_card_context_map]] | upstream | 0.43 |
| [[p11_qg_context_map]] | downstream | 0.41 |
| [[bld_instruction_context_map]] | upstream | 0.41 |
