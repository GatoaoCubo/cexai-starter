---
kind: config
id: bld_config_consolidation_policy
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for consolidation_policy production
quality: null
title: "Config: consolidation_policy-builder"
version: "2.0.0"
author: n06_commercial
tags:
  - "consolidation_policy"
  - "builder"
  - "config"
tldr: "Naming convention p10_cp_*, pillar P10, max 6144 bytes, stored in P10_memory/ or agent-specific subdirectory"
domain: "LLM agent memory consolidation"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords:
  - "limits for consolidation_policy production"
  - "llm agent memory consolidation"
  - "naming convention p"
  - "pillar p"
  - "stored in p"
  - "or agent-specific subdirectory"
  - "consolidation_policy"
  - "builder"
  - "config"
  - "p10_cp_[a-z][a-z0-9_]+"
density_score: 0.90
related:
  - bld_config_procedural_memory
  - bld_config_memory_architecture
  - bld_config_agents_md
  - bld_config_safety_policy
  - bld_config_agent_profile
---

## Naming Convention
Pattern: `p10_cp_[a-z][a-z0-9_]+`
Examples:
- `p10_cp_customer_support_pro`
- `p10_cp_research_agent_enterprise`
- `p10_cp_minimal_ttl_only`

## Paths
Artifacts stored in pillar directory:
`P10_memory/policies/`

Or co-located with parent memory_architecture:
`N0{x}_*/memory/p10_cp_*.md`

## Limits
- max_bytes: 6144
- max_turns: null (static policy spec)
- effort_level: 4 (high -- requires reading parent memory_architecture first)
- quality_floor: 8.0
- quality_target: 9.0

## Hooks
- pre_build: read parent memory_architecture artifact to determine active layers + tier
- post_build: `python _tools/cex_compile.py {path}`
- on_quality_fail: check domain accuracy first (D04 contamination is most common failure)
- on_error: verify consolidation_async: true is set and no OS/GC terminology present

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_procedural_memory]] | sibling | 0.45 |
| [[bld_config_memory_architecture]] | sibling | 0.37 |
| [[bld_config_agents_md]] | sibling | 0.27 |
| [[bld_config_safety_policy]] | sibling | 0.27 |
| [[bld_config_agent_profile]] | sibling | 0.26 |
