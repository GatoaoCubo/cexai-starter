---
kind: config
id: bld_config_realtime_session
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for realtime_session production
quality: null
title: "Config: realtime-session-builder"
version: "1.1.0"
author: n01_audit
tags: [realtime_session, builder, config]
tldr: "Naming, paths, limits for realtime_session production (kind lives in P04, artifacts use p04_rs_ prefix)."
domain: "realtime_session construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for realtime_session production, realtime_session construction, kind lives in p, artifacts use p, rs_ prefix, realtime_session, builder, config, "p04_rs_{{name}}.md", p04_rs_support_voicebot.md]
density_score: 0.88
related:
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_collaboration_pattern
  - bld_config_transport_config
  - bld_config_agents_md
---

## Naming Convention
Pattern: `p04_rs_{{name}}.md`
Examples: `p04_rs_support_voicebot.md`, `p04_rs_demo_agent.md`
Regex: `^p04_rs_[a-z0-9_]{3,48}\.md$`

Note: Kind `realtime_session` lives in pillar P04 (Tools/Capabilities).
The `bld_config` ISO itself lives in P09 (Config) as it defines production settings.

## Paths
Artifacts: `P04_tools/realtime_session/p04_rs_{{name}}.md`
Builder ISOs: `archetypes/builders/realtime-session-builder/`

## Limits
max_bytes: 5120
max_turns: 20
effort_level: 5

## Hooks
pre_build: null
post_build: python _tools/cex_compile.py {path}
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Realtime session config |
| Dependencies | session_state, session_backend |
| Primary 8F function | F6_produce |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency session_state not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | realtime session construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_ab_test_config]] | sibling | 0.50 |
| [[bld_config_collaboration_pattern]] | sibling | 0.49 |
| [[bld_config_transport_config]] | sibling | 0.47 |
| [[bld_config_agents_md]] | sibling | 0.47 |
