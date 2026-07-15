---
kind: schema
id: bld_schema_memory_scope
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema — SINGLE SOURCE OF TRUTH for memory_scope
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Memory Scope"
version: "1.0.0"
author: n03_builder
tags:
  - "memory_scope"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for memory scope construction, demonstrating ideal structure and common pitfalls."
domain: "memory scope construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords:
  - "formal schema"
  - "memory scope construction"
  - "schema memory scope"
  - "memory_scope"
  - "builder"
  - "examples"
  - "^p02_memscope_[a-z][a-z0-9_]+$"
  - "## overview"
  - "## memory types"
  - "## backend config"
density_score: 0.90
related:
  - bld_schema_retriever_config
  - bld_schema_handoff_protocol
  - bld_schema_output_validator
  - bld_schema_constraint_spec
  - bld_schema_chunk_strategy
---

# Schema: memory_scope
## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p02_memscope_{slug}) | YES | - | Namespace compliance |
| kind | literal "memory_scope" | YES | - | Type integrity |
| pillar | literal "P02" | YES | - | Pillar assignment |
| version | semver string | YES | "1.0.0" | Artifact versioning |
| created | date YYYY-MM-DD | YES | - | Created date |
| updated | date YYYY-MM-DD | YES | - | Updated date |
| author | string | YES | - | Producer identity |
| name | string | YES | - | Human-readable name |
| memory_types | string | YES | - | Memory types |
| backend | string | YES | - | Backend |
| ttl | string | YES | - | Ttl |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | - | Must include "memory_scope" |
| tldr | string <= 160ch | YES | - | Dense summary |
| description | string | REC | - | Description |
| scope | string | REC | - | Scope |
| max_entries | string | REC | - | Max entries |
| eviction_policy | string | REC | - | Eviction policy |
| encryption | string | REC | - | Encryption |
| shared_with | string | REC | - | Shared with |
## ID Pattern
Regex: `^p02_memscope_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.
## Body Structure (required sections)
1. `## Overview` — overview specification
2. `## Memory Types` — memory types specification
3. `## Backend Config` — backend config specification
4. `## Lifecycle` — lifecycle specification
## Constraints
- max_bytes: 2048 (body only)
- naming: p02_memscope_{slug}.md (single file)
- machine_format: yaml (compiled artifact)
- id == filename stem
- quality: null always
- density_min: 0.8

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_retriever_config]] | sibling | 0.72 |
| [[bld_schema_handoff_protocol]] | sibling | 0.70 |
| [[bld_schema_output_validator]] | sibling | 0.70 |
| [[bld_schema_constraint_spec]] | sibling | 0.69 |
| [[bld_schema_chunk_strategy]] | sibling | 0.68 |
