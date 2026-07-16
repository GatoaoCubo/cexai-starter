---
kind: tools
id: bld_tools_reranker_config
pillar: P04
llm_function: CALL
purpose: Tools available for reranker_config production
quality: null
title: "Tools Reranker Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [reranker_config, builder, tools]
tldr: "Tools available for reranker_config production"
domain: "reranker_config construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [reranker_config construction, tools reranker config, reranker_config, builder, tools, production tools, validation tools, external references, cohere rerank, related artifacts]
density_score: 0.85
related:
  - bld_tools_rbac_policy
  - bld_tools_github_issue_template
  - bld_tools_usage_quota
  - bld_tools_graph_rag_config
  - bld_tools_agentic_rag
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile reranker_config artifact to .yaml | After authoring |
| cex_score.py | Peer-review score via 5D rubric | After compile |
| cex_retriever.py | Find similar existing reranker_config artifacts | During F3 INJECT |
| cex_doctor.py | Validate builder ISO health | Pre-dispatch |
| cex_wave_validator.py | Validate all ISOs in builder directory | Post-build |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_hooks.py | Pre-commit quality gate enforcement | Before git commit |
| cex_sanitize.py | Check ASCII compliance in code files | Pre-commit |
| cex_hygiene.py | Artifact CRUD rules (frontmatter, naming) | Periodic cleanup |

## External References
- Cohere Rerank v3 (cross-encoder reranking API)
- BGE reranker (BAAI/bge-reranker-large via HuggingFace)
- ColBERT v2 (late-interaction neural ranking, Stanford NLP)
- ms-marco cross-encoders (ms-marco-MiniLM-L-6-v2, msmarco-distilbert)
- RankGPT (GPT-4 listwise reranking, Sun et al. 2023)
- FAISS (vector similarity search, Facebook AI)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_rbac_policy]] | sibling | 0.39 |
| [[bld_tools_github_issue_template]] | sibling | 0.38 |
| [[bld_tools_usage_quota]] | sibling | 0.38 |
| [[bld_tools_graph_rag_config]] | sibling | 0.38 |
| [[bld_tools_agentic_rag]] | sibling | 0.38 |
