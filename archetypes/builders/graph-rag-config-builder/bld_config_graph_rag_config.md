---
kind: config
id: bld_config_graph_rag_config
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for graph_rag_config production
quality: null
title: "Config Graph Rag Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [graph_rag_config, builder, config]
tldr: "Production constraints for graph rag config: naming (p01_grc_{{name}}.yaml), output paths (P01/), size limit 4096B. Graph RAG config."
domain: "graph_rag_config construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for graph_rag_config production, graph_rag_config construction, config graph rag config, output paths, size limit, graph rag config, graph_rag_config, builder, config, p01_grc_<name>.yaml]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_agents_md
  - bld_config_collaboration_pattern
  - bld_config_transport_config
---

## Naming Convention
Pattern: `p01_grc_<name>.yaml`
Examples: `p01_grc_knowledge.yaml`, `p01_grc_finance.yaml`

## Paths
Artifacts: `/mnt/cex/data/artifacts/rag_configs/`
Logs: `/var/log/cex/rag_builder/`
Cache: `/tmp/cex/rag_cache/`

## Limits
max_bytes: 4096
max_turns: 5
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Graph RAG config |
| Dependencies | rag_source, embedding_config, vector_store |
| Primary 8F function | F3_inject |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency rag_source not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | graph rag config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_ab_test_config]] | sibling | 0.53 |
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_agents_md]] | sibling | 0.48 |
| [[bld_config_collaboration_pattern]] | sibling | 0.48 |
| [[bld_config_transport_config]] | sibling | 0.48 |
