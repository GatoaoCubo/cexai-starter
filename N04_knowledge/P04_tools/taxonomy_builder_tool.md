---
id: p04_cli_taxonomy_builder_n04
kind: cli_tool
8f: F5_call
pillar: P04
title: "Taxonomy Builder -- Kind Registry & Classification Engine"
version: 1.0.0
created: 2026-04-07
author: n04_knowledge
domain: taxonomy-management
quality: null
tags: [tool, n04, taxonomy, classification, kind-registry, tag-normalization]
tldr: "CLI tool to build and maintain taxonomies: kind tree visualization, tag normalization, orphan detection, pillar coverage reports."
keywords: [taxonomy builder, kind registry, classification engine, kind tree visualization, tag normalization, orphan detection, pillar coverage reports, tool, taxonomy, classification]
density_score: 0.90
related:
  - bld_architecture_kind
---

# Taxonomy Builder Tool

> **Status: proposed specification (not yet implemented).** No `_tools/taxonomy_builder.py` exists in this repo today -- confirmed via `git log --all --full-history` (the path has never been committed to this repository). Everything below is the target design: CLI surface, taxonomy tree format, tag-normalization rules, orphan-detection criteria, and coverage metrics for a tool that has not been built. Note: `_tools/cex_taxonomy_scout.py` is a different, already-implemented tool -- it discovers NEW candidate kinds from external sources (GitHub/arXiv/IETF/W3C); it does not build or audit the existing kind registry described here.

## Purpose

Constructs, maintains, and audits the CEXAI taxonomy. Turns the flat kind registry (300+ kinds) into navigable trees, detects classification anomalies, and enforces tag normalization rules.

## Usage

**All commands below (proposed, not yet implemented):**

```bash
# PROPOSED, not yet implemented -- generate taxonomy tree (visual)
python _tools/taxonomy_builder.py tree --output N04_knowledge/P05_output/taxonomy_tree.md

# PROPOSED, not yet implemented -- normalize tags across all artifacts
python _tools/taxonomy_builder.py normalize --scope P01_knowledge/ --dry-run

# PROPOSED, not yet implemented -- detect orphan artifacts (no valid kind or pillar)
python _tools/taxonomy_builder.py orphans --all

# PROPOSED, not yet implemented -- pillar coverage report
python _tools/taxonomy_builder.py coverage --output N04_knowledge/P05_output/pillar_coverage.md

# PROPOSED, not yet implemented -- kind distribution (count per kind)
python _tools/taxonomy_builder.py distribution
```

## Taxonomy Tree Format

```
CEXAI (N artifacts)
+-- P01 Knowledge (10 kinds, N compiled)
|   +-- knowledge_card (N)
|   +-- glossary_entry (N)
|   +-- few_shot_example (0) <- GAP
|   +-- context_doc (N)
|   +-- rag_source (N)
|   +-- embedding_config (N)
|   +-- chunk_strategy (N)
|   +-- retriever_config (N)
|   +-- embedder_provider (N)
|   +-- vector_store (N)
+-- P02 Model (11 kinds, ...)
|   +-- ...
+-- P12 Orchestration (8 kinds, ...)
    +-- ...
```

## Tag Normalization Rules

| Rule | Example | Canonical Form |
|------|---------|---------------|
| Lowercase | `RAG`, `Rag` | `rag` |
| Kebab-case | `knowledge card`, `knowledge_card` | `knowledge-card` |
| Max 3 words | `large-language-model-prompting` | `llm-prompting` |
| Dedup synonyms | `llm` + `large-language-model` | Keep `llm` (shorter) |
| No kind echo | `kind: knowledge_card`, tag: `knowledge-card` | Remove tag |
| No pillar echo | `pillar: P01`, tag: `p01` | Remove tag |

## Orphan Detection

An artifact is orphaned if ANY of:
- `kind` not in `.cex/kinds_meta.json`
- `pillar` doesn't match `P{01-12}`
- No builder exists in `archetypes/builders/{kind}-builder/`
- No sub-agent exists in `.claude/agents/{kind}-builder.md`
- File is in wrong nucleus directory for its kind

## Coverage Metrics

| Metric | Formula | Healthy |
|--------|---------|---------|
| Kind coverage | `kinds_with_artifacts / total_kinds` | >80% |
| Pillar balance | `stdev(artifacts_per_pillar) / mean` | <0.5 |
| Tag entropy | `-sum(p(tag) log p(tag))` | >4.0 (diverse) |
| Orphan rate | `orphans / total_artifacts` | <5% |

## Boundary

One-shot CLI tool. Not a skill (no phases) or daemon (no background persistence).

## 8F Pipeline Function

Primary function: **CALL**

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_kind]] | downstream | 0.28 |
