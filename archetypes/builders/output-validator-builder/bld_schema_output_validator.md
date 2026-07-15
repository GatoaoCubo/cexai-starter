---
kind: schema
id: bld_schema_output_validator
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema — SINGLE SOURCE OF TRUTH for output_validator
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Output Validator"
version: "1.0.0"
author: n03_builder
tags:
  - "output_validator"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for output validator construction, demonstrating ideal structure and common pitfalls."
domain: "output validator construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords:
  - "formal schema"
  - "output validator construction"
  - "schema output validator"
  - "output_validator"
  - "builder"
  - "examples"
  - "^p05_oval_[a-z][a-z0-9_]+$"
  - "## overview"
  - "## checks"
  - "## failure actions"
density_score: 0.90
related:
  - bld_schema_retriever_config
  - bld_schema_handoff_protocol
  - bld_schema_memory_scope
  - bld_schema_constraint_spec
  - bld_schema_chunk_strategy
---

# Schema: output_validator
## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p05_oval_{slug}) | YES | - | Namespace compliance |
| kind | literal "output_validator" | YES | - | Type integrity |
| pillar | literal "P05" | YES | - | Pillar assignment |
| version | semver string | YES | "1.0.0" | Artifact versioning |
| created | date YYYY-MM-DD | YES | - | Created date |
| updated | date YYYY-MM-DD | YES | - | Updated date |
| author | string | YES | - | Producer identity |
| name | string | YES | - | Human-readable name |
| checks | string | YES | - | Checks |
| on_fail | string | YES | - | On fail |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | - | Must include "output_validator" |
| tldr | string <= 160ch | YES | - | Dense summary |
| description | string | REC | - | Description |
| retry_count | string | REC | - | Retry count |
| fix_prompt | string | REC | - | Fix prompt |
| severity | string | REC | - | Severity |
| applies_to | string | REC | - | Applies to |
## ID Pattern
Regex: `^p05_oval_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.
## Body Structure (required sections)
1. `## Overview` — overview specification
2. `## Checks` — checks specification
3. `## Failure Actions` — failure actions specification
4. `## Integration` — integration specification
## Constraints
- max_bytes: 2048 (body only)
- naming: p05_oval_{slug}.md (single file)
- machine_format: yaml (compiled artifact)
- id == filename stem
- quality: null always
- density_min: 0.85

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_retriever_config]] | sibling | 0.71 |
| [[bld_schema_handoff_protocol]] | sibling | 0.70 |
| [[bld_schema_memory_scope]] | sibling | 0.69 |
| [[bld_schema_constraint_spec]] | sibling | 0.69 |
| [[bld_schema_chunk_strategy]] | sibling | 0.68 |
