---
id: n04_rs_cex_codebase
title: "Rag Source Knowledge"
kind: rag_source
8f: F3_inject
pillar: P01
version: "2.1.0"
created: "2024-03-30"
updated: "2026-05-02"
author: "N04 Knowledge Nucleus"
url: "file://./"
domain: "CEX Internals"
last_checked: "2026-05-02"
quality: null
tags: [rag-source, n04, knowledge, codebase, markdown, p01, internal]
tldr: "The CEX project's own codebase as a RAG source: all Markdown files (~3,612 artifacts), indexed by cex_retriever.py. Primary source for any query about CEX architecture, processes, or artifacts."
keywords: [cex, codebase, markdown, documentation, artifacts, rag-source, file-glob, internal-knowledge]
reliability: "high"
format: "markdown"
extraction_method: "file_glob"
density_score: null
related:
  - bld_memory_rag_source
  - bld_collaboration_rag_source
  - bld_architecture_rag_source
  - bld_knowledge_card_rag_source
  - p03_ins_rag_source
  - p01_gl_rag
  - rag_source_supabase
  - retriever_config_knowledge
---

# RAG Source: CEX Codebase (Markdown)

## 1. Source Description
This RAG source encompasses the entire local CEX project directory, with a specific focus on Markdown (`.md`) files. These files constitute the primary, most up-to-date source of truth for all CEX architecture, processes, artifacts, and documentation. They are the living memory of the system.

## 2. Extraction Method: `file_glob`
- **Description**: The `document_loaders` MCP (and `cex_retriever.py`) use a file globbing mechanism to find all relevant files within the project directory specified by the `url`.
- **Configuration**:
  - **Glob Pattern**: `**/*.md`
  - **Exclude Patterns**:
    - `**/node_modules/**`
    - `**/_archive/**`
    - `**/.git/**`
    - `**/compiled/**` (auto-generated YAML mirrors -- redundant)
    - `**/.cex/runtime/**` (ephemeral handoffs / signals)

## 3. Freshness & Update Policy

| Aspect | Details |
|--------|---------|
| **Re-check Interval** | Real-time (per-commit) |
| **Trigger Method** | Git pre-commit hook on `.md` file modifications |
| **Update Process** | Document Ingestion & Indexing workflow for the specific modified file |
| **Sync Guarantee** | Perfect alignment between committed codebase state and searchable knowledge base |
| **Staleness Risk** | Eliminated for internal documentation |

## 4. Reliability & Authority
- **Reliability**: `High`. As the direct output of the CEX nuclei, these documents are considered canonical, authoritative sources of information.
- **Verification**: The content is implicitly verified by the peer review process of pull requests and the operational success of the described systems.
- **Provenance**: Every artifact has frontmatter with `author`, `created`, `updated` for full lineage tracing.

## 5. Integration

### Consumers
This source is consumed by:
- `cex_retriever.py` -- TF-IDF sparse index (Phase 1 of preflight)
- `cex_preflight.py` -- composes Phase 1 + Phase 2 (Haiku rerank)
- `/build` skill -- Template-First match scan
- `/grid` -- spec compiler retrieves examples
- `cex_evolve.py` -- AutoResearch loop reads similar artifacts

### Priority signals
The `retriever_config` boosts this source when the user's query contains:
- Capital `CEX` / `CEXAI`
- Nucleus codes `N00`-`N07`
- Pillar codes `P01`-`P12`
- Kind names from `.cex/kinds_meta.json` (125 kinds)
- Builder names ending in `-builder`

## 6. Counter-Examples (when NOT to use this source)

| Query type | Better source | Reason |
|------------|---------------|--------|
| Latest LLM provider pricing | web search via N07 MCP | this corpus is internal, not external market data |
| Current Python package versions | `pip show` / requirements.txt | this corpus describes patterns, not pinned versions |
| Live system status | `cex_doctor.py` runtime | this corpus is static doc, not telemetry |
| Customer-specific data | external CRM | by policy, no PII in repo |

## 7. Related Sources

- `rag_source_supabase` -- planned dense-vector mirror of this corpus in Supabase pgvector
- `p10_bi_bm25_knowledge` -- the BM25/TF-IDF index built FROM this source

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_rag_source]] | related | 0.32 |
| [[bld_orchestration_rag_source]] | related | 0.28 |
| [[bld_architecture_rag_source]] | related | 0.26 |
| [[bld_knowledge_rag_source]] | related | 0.25 |
| [[p03_ins_rag_source]] | related | 0.25 |
| [[p01_gl_rag]] | upstream | 0.32 |
| rag_source_supabase | sibling | 0.50 |
| retriever_config_knowledge | downstream | 0.40 |
