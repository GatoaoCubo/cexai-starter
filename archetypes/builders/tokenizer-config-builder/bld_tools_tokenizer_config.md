---
kind: tools
id: bld_tools_tokenizer_config
pillar: P04
llm_function: CALL
purpose: Tools available for tokenizer_config production
quality: null
title: "Tokenizer Config Builder - Tools ISO"
version: "1.0.0"
author: n03_builder
tags: [tokenizer_config, builder, tools]
tldr: "Tool registry for tokenizer config builder: CEX pipeline tools (compile, score, retrieve), file system ops (Read/Write/Edit/Glob/Grep), and domain-specific automation for bpe, sentencepiece, or tiktoken tokenizer parameters and vocabulary configuration."
domain: "tokenizer configuration"
created: "2026-04-23"
updated: "2026-04-23"
8f: "F5_call"
keywords: [tokenizer configuration, cex pipeline tools, file system ops, tokenizer_config, builder, tools, production tools, data sources, tool permissions, pipeline tools]
density_score: 0.85
related:
  - bld_tools_query_optimizer
  - bld_tools_inference_config
  - bld_tools_synthetic_data_config
  - bld_tools_curriculum_config
  - bld_tools_distillation_config
---
# Tools: tokenizer-config-builder

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
| tiktoken docs | github.com/openai/tiktoken | OpenAI tokenizer specs |
| SentencePiece docs | github.com/google/sentencepiece | Google tokenizer specs |
| HF Tokenizers | huggingface.co/docs/tokenizers | HuggingFace tokenizer library |

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
| Domain | tokenizer config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_query_optimizer]] | sibling | 0.57 |
| [[bld_tools_inference_config]] | sibling | 0.54 |
| [[bld_tools_synthetic_data_config]] | sibling | 0.52 |
| [[bld_tools_curriculum_config]] | sibling | 0.51 |
| [[bld_tools_distillation_config]] | sibling | 0.50 |
