---
kind: schema
id: bld_schema_retriever_config
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema — SINGLE SOURCE OF TRUTH for retriever_config
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Retriever Config"
version: "1.0.0"
author: n03_builder
tags:
  - "retriever_config"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for retriever config construction, demonstrating ideal structure and common pitfalls."
domain: "retriever config construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords:
  - "formal schema"
  - "retriever config construction"
  - "schema retriever config"
  - "retriever_config"
  - "builder"
  - "examples"
  - "^p01_retr_[a-z][a-z0-9_]+$"
  - "## overview"
  - "## search strategy"
  - "## parameters"
density_score: 0.90
related:
  - bld_schema_output_validator
  - bld_schema_handoff_protocol
  - bld_schema_memory_scope
  - bld_schema_chunk_strategy
  - bld_schema_constraint_spec
---

# Schema: retriever_config
## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p01_retr_{slug}) | YES | - | Namespace compliance |
| kind | literal "retriever_config" | YES | - | Type integrity |
| pillar | literal "P01" | YES | - | Pillar assignment |
| version | semver string | YES | "1.0.0" | Artifact versioning |
| created | date YYYY-MM-DD | YES | - | Created date |
| updated | date YYYY-MM-DD | YES | - | Updated date |
| author | string | YES | - | Producer identity |
| name | string | YES | - | Human-readable name |
| store_type | string | YES | - | Store type |
| top_k | string | YES | - | Top k |
| search_type | string | YES | - | Search type |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | - | Must include "retriever_config" |
| tldr | string <= 160ch | YES | - | Dense summary |
| description | string | REC | - | Description |
| hybrid_ratio | string | REC | - | Hybrid ratio |
| reranker | string | REC | - | Reranker |
| filters | string | REC | - | Filters |
| score_threshold | string | REC | - | Score threshold |
| fetch_k | string | REC | - | Fetch k |
## ID Pattern
Regex: `^p01_retr_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.
## Body Structure (required sections)
1. `## Overview` — overview specification
2. `## Search Strategy` — search strategy specification
3. `## Parameters` — parameters specification
4. `## Integration` — integration specification
## Constraints
- max_bytes: 2048 (body only)
- naming: p01_retr_{slug}.md (single file)
- machine_format: yaml (compiled artifact)
- id == filename stem
- quality: null always
- density_min: 0.8

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_output_validator]] | sibling | 0.71 |
| [[bld_schema_handoff_protocol]] | sibling | 0.71 |
| [[bld_schema_memory_scope]] | sibling | 0.70 |
| [[bld_schema_chunk_strategy]] | sibling | 0.70 |
| [[bld_schema_constraint_spec]] | sibling | 0.70 |
