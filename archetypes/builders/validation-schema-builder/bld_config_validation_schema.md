---
kind: config
id: bld_config_validation_schema
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for validation_schema production
pattern: CONFIG restricts SCHEMA, never contradicts
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Validation Schema"
version: "1.0.0"
author: n03_builder
tags: [validation_schema, builder, examples]
tldr: "Golden and anti-examples for validation schema construction, demonstrating ideal structure and common pitfalls."
domain: "validation schema construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [limits for validation_schema production, validation schema construction, config validation schema, validation_schema, builder, examples, production rules, file paths, size limits, format policy]
density_score: 0.90
related:
  - bld_config_quality_gate
  - bld_config_memory_scope
  - bld_config_retriever_config
  - bld_config_response_format
  - bld_config_prompt_version
---
# Config: validation_schema Production Rules
## Naming
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact | p06_vs_{scope}.yaml | p06_vs_knowledge_card.yaml |
| Builder dir | kebab-case | validation-schema-builder/ |
| Fields | snake_case | target_kind, on_failure, fields_count |
| Scope slugs | lowercase_underscores | knowledge_card, model_card, signal |
Rule: id MUST equal filename stem.
## File Paths
1. Output: cex/P06_schema/examples/p06_vs_{scope}.yaml
2. Compiled: cex/P06_schema/compiled/p06_vs_{scope}.json
## Size Limits (aligned with SCHEMA)
1. Body: max 3072 bytes
2. Density: >= 0.80
3. Fields: >= 1 (no upper limit, but 5-20 typical)
## Format Policy
1. machine_format: json (the schema itself is a JSON-compatible contract)
2. Target output may be json or yaml (specified in format field)
3. Field types MUST be JSON Schema compatible
4. Constraints use simple operators (pattern, enum, min, max, min_length, max_length)

## Metadata

```yaml
id: bld_config_validation_schema
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-config-validation-schema.md
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | validation schema construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_quality_gate | sibling | 0.35 |
| [[bld_config_memory_scope]] | sibling | 0.35 |
| [[bld_config_retriever_config]] | sibling | 0.33 |
| [[bld_config_response_format]] | sibling | 0.31 |
| [[bld_config_prompt_version]] | sibling | 0.31 |
