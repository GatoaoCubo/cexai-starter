---
quality: null
quality: null
id: kc_context_map
kind: knowledge_card
8f: F3_inject
pillar: P01
title: "Knowledge Card -- Context Map"
version: 1.0.0
tags: [knowledge, context_map, ddd, bounded-context, strategic-design]
tldr: "DDD artifact mapping upstream/downstream relationships between bounded contexts"
when_to_use: "When documenting integration patterns and coupling between multiple bounded contexts or teams"
keywords: [bounded context, anti-corruption layer, open host service, ubiquitous language, domain-driven design, context map, translation mechanisms, team coordination patterns]
density_score: 1.0
updated: "2026-04-22"
related:
  - bld_knowledge_card_context_map
  - context-map-builder
  - bld_architecture_context_map
  - bld_schema_context_map
  - p10_lr_context_map_builder
---

# Context Map

## Definition

A `context_map` is a Domain-Driven Design (DDD) artifact that documents the relationships and integration patterns between bounded contexts (BCs). It maps upstream/downstream coupling, translation mechanisms (Anti-Corruption Layer, Open Host Service), and team coordination patterns. Introduced by Eric Evans in "Domain-Driven Design" (2003) as a mandatory strategic design exercise for complex multi-team systems.

Not bounded_context (single BC definition and ubiquitous language). Not component_map (deployment topology and infrastructure).

## When to Use

| Scenario | Use context_map? |
|----------|-----------------|
| Multiple teams with separate domain models | YES |
| Service integration architecture review | YES |
| Identifying anti-corruption needs (legacy/new system) | YES |
| Onboarding developers to system relationships | YES |
| Single BC documentation | NO -- use bounded_context |
| Service deployment diagram | NO -- use component_map |
| Code-level architecture | NO -- use diagram |

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| system_name | string | YES | Name of the system being mapped |
| contexts_count | integer | YES | Number of BCs in scope |
| contexts | table | YES | BC names, teams, and descriptions |
| relationships | table | YES | Upstream/downstream pairs with DDD patterns |
| pattern | enum | YES | ACL/OHS/Conformist/Partnership/Shared_Kernel |
| integration_type | enum | REC | sync/async/batch |
| team_coupling | table | REC | Coupling level + risk + mitigation |

## DDD Patterns

| Pattern | Coupling | When to Use |
|---------|----------|-------------|
| ACL | Low | Protect downstream from upstream model rot |
| OHS | Low | Upstream exposes formal versioned protocol |
| Conformist | HIGH | Small team, temporary simplicity tradeoff |
| Partnership | Very High | Two teams co-evolving together |
| Shared Kernel | Very High | Shared code subset (high maintenance cost) |
| Customer/Supplier | Medium | Downstream negotiates upstream backlog |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Unlabeled "integration" relationships | No coupling insight | Use DDD pattern names |
| Conformist everywhere | Upstream lock-in | Plan ACL migration |
| Missing team ownership | Governance gap | Assign owning team per BC |
| Mixing with component_map | Strategic vs tactical confusion | Separate artifacts |

## Cross-Framework Map

| Framework/Method | Equivalent | Notes |
|-----------------|-----------|-------|
| Evans DDD (2003) | context_map | Origin -- canonical reference |
| Team Topologies | Stream-aligned + platform map | Organizational lens |
| C4 Model L1 (System Context) | context_map | Technical implementation |
| Microservices dependency map | context_map | Implementation-level view |

## Decision Tree

```
Documenting BC relationships?
  YES -> context_map
    Downstream adopts upstream model directly?
      YES -> Conformist (flag HIGH coupling risk)
      NO:
        Upstream has formal API/protocol?
          YES -> OHS
          Downstream builds translation layer?
            YES -> ACL (recommended)
            NO  -> Partnership (joint evolution)
```

## Integration

- Documents: bounded_context (P08) -- each node in the map
- Influences: interface (P08) -- ACL/OHS become formal interfaces
- Informs: workflow (P12) -- workflows cross context boundaries
- Feeds: decision_record (P08) -- architectural decisions about patterns
- Pillar: P08 (Architecture) -- strategic design documentation

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_context_map]] | sibling | 0.70 |
| [[context-map-builder]] | downstream | 0.52 |
| [[bld_architecture_context_map]] | downstream | 0.49 |
| [[bld_schema_context_map]] | downstream | 0.48 |
| [[p10_lr_context_map_builder]] | downstream | 0.42 |
