---
kind: tools
id: bld_tools_distillation_config
pillar: P04
llm_function: CALL
purpose: Tools available for distillation_config production
quality: null
title: "Distillation Config Builder - Tools ISO"
version: "1.0.0"
author: n03_builder
tags: [distillation_config, builder, tools]
tldr: "Tool registry for distillation config builder: CEX pipeline tools (compile, score, retrieve), file system ops (Read/Write/Edit/Glob/Grep), and domain-specific automation for teacher-student model compression and knowledge distillation setup."
domain: "model distillation"
created: "2026-04-23"
updated: "2026-04-23"
8f: "F5_call"
keywords: [model distillation, cex pipeline tools, file system ops, distillation_config, builder, tools, production tools, data sources, tool permissions, pipeline tools]
density_score: 0.85
related:
  - bld_tools_synthetic_data_config
  - bld_tools_query_optimizer
  - bld_tools_curriculum_config
  - bld_tools_inference_config
  - bld_tools_retrieval_evaluator
---
# Tools: distillation-config-builder

## Production Tools

| Tool | Purpose | When | Status |
|------|---------|------|--------|
| cex_compile.py | Compile artifact to YAML | Phase 3 | ACTIVE |
| cex_score.py | Score artifact quality | Phase 3 | ACTIVE |
| cex_retriever.py | Find similar configs | Phase 1 | ACTIVE |
| cex_doctor.py | Health check | Phase 3 | ACTIVE |

## Data Sources

| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P02_model/_schema.yaml | Field definitions |
| Hinton 2015 | arxiv.org/abs/1503.02531 | Original KD paper |
| DistilBERT | arxiv.org/abs/1910.01108 | BERT distillation reference |

## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Permitted |
| DENIED | (none) | -- |

## CEX Pipeline Tools

| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile .md artifact to .yaml | After Write (F8) |
| cex_score.py | Peer-review quality scoring | After production (F7) |
| cex_retriever.py | Discover similar artifacts by TF-IDF | During F3 INJECT |
| cex_doctor.py | Health check builder ISOs | Before dispatch |

## Properties

| Property | Value |
|----------|-------|
| Kind | `tools` |
| Pillar | P04 |
| Domain | distillation config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_synthetic_data_config]] | sibling | 0.64 |
| [[bld_tools_query_optimizer]] | sibling | 0.64 |
| [[bld_tools_curriculum_config]] | sibling | 0.63 |
| [[bld_tools_inference_config]] | sibling | 0.53 |
| [[bld_tools_retrieval_evaluator]] | sibling | 0.49 |
