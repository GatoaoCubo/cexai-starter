---
kind: config
id: bld_config_mcp_app_extension
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for mcp_app_extension production
quality: null
title: "Config MCP App Extension"
version: "1.0.0"
author: wave7_n03_dev_manifests
tags: [mcp_app_extension, builder, config]
tldr: "Production constraints for mcp app extension: naming (p04_mae_{{name}}.md), output paths (P04/), size limit 4096B. MCP Apps Extension app."
domain: "mcp_app_extension construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for mcp_app_extension production, mcp_app_extension construction, config mcp app extension, output paths, size limit, mcp apps extension app, mcp_app_extension, builder, config, "p04_mae_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_search_strategy
  - bld_config_agents_md
  - bld_config_collaboration_pattern
  - bld_config_agent_profile
---

## Naming Convention
Pattern: `p04_mae_{{name}}.md`
Examples: `p04_mae_figma_design_inspector.md`, `p04_mae_notion_workspace_ui.md`

## Paths
Artifacts stored in: `/artifacts/p04/mcp_app_extensions/{{name}}.md`

## Limits
max_bytes: 4096
max_turns: 6
effort_level: 4

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | MCP Apps Extension app |
| Dependencies | mcp_server, api_client |
| Primary 8F function | F5_call |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency mcp_server not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | mcp app extension construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.55 |
| [[bld_config_search_strategy]] | sibling | 0.54 |
| [[bld_config_agents_md]] | sibling | 0.54 |
| [[bld_config_collaboration_pattern]] | sibling | 0.51 |
| [[bld_config_agent_profile]] | sibling | 0.51 |
