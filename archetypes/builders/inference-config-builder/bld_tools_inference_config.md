---
kind: tools
id: bld_tools_inference_config
pillar: P04
llm_function: CALL
purpose: Tools available for inference_config production
quality: null
title: "Inference Config Builder - Tools ISO"
version: "1.0.0"
author: n03_builder
tags: [inference_config, builder, tools]
tldr: "Tool registry for inference config builder: CEX pipeline tools (compile, score, retrieve), file system ops (Read/Write/Edit/Glob/Grep), and domain-specific automation for inference-time parameters: temperature, top_p, sampling strategy, stop sequences, penalties."
domain: "model inference"
created: "2026-04-23"
updated: "2026-04-23"
8f: "F5_call"
keywords: [model inference, cex pipeline tools, file system ops, sampling strategy, stop sequences, inference_config, builder, tools, production tools, data sources]
density_score: 0.85
related:
  - bld_tools_query_optimizer
  - bld_tools_synthetic_data_config
  - bld_tools_curriculum_config
  - bld_tools_distillation_config
  - bld_tools_retrieval_evaluator
---
# Tools: inference-config-builder

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
| CEX Schema | P09_config/_schema.yaml | Field definitions |
| vLLM docs | vllm.readthedocs.io | vLLM serving framework |
| llama.cpp | github.com/ggerganov/llama.cpp | GGUF quantization specs |
| Ollama docs | ollama.com/docs | Local model serving |

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
| Domain | inference config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_query_optimizer]] | sibling | 0.59 |
| [[bld_tools_synthetic_data_config]] | sibling | 0.54 |
| [[bld_tools_curriculum_config]] | sibling | 0.53 |
| [[bld_tools_distillation_config]] | sibling | 0.52 |
| [[bld_tools_retrieval_evaluator]] | sibling | 0.48 |
