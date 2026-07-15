---
kind: config
id: bld_config_retriever_config
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
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
title: "Config Retriever Config"
version: "1.0.0"
author: n03_builder
tags: [retriever_config, builder, examples]
tldr: "Golden and anti-examples for retriever config construction, demonstrating ideal structure and common pitfalls."
domain: "retriever config construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, retriever config construction, config retriever config, retriever_config, builder, examples, "p01_retr_{slug}.md"]
density_score: 0.90
related:
  - bld_config_memory_scope
  - bld_config_prompt_version
  - bld_config_output_validator
  - bld_config_handoff_protocol
  - bld_config_constraint_spec
---
# Config: retriever_config Production Rules
## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p01_retr_{slug}.md` | `p01_retr_example.md` |
| Builder directory | kebab-case | `retriever-config-builder/` |
| Frontmatter fields | snake_case | id, kind, pillar |
| Slug | snake_case, lowercase, no hyphens | `example_config` |
Rule: id MUST equal filename stem. Hyphens in id = HARD FAIL.
## File Paths
1. Output: `cex/P01_knowledge/examples/p01_retr_{slug}.md`
2. Compiled: `cex/P01_knowledge/compiled/p01_retr_{slug}.yaml`
## Size Limits (aligned with SCHEMA)
1. Body: max 2048 bytes
2. Total (frontmatter + body): ~3048 bytes
3. Density: >= 0.8 (no filler)

## Metadata

```yaml
id: bld_config_retriever_config
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-config-retriever-config.md
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | retriever config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_memory_scope]] | sibling | 0.56 |
| [[bld_config_prompt_version]] | sibling | 0.55 |
| [[bld_config_output_validator]] | sibling | 0.54 |
| [[bld_config_handoff_protocol]] | sibling | 0.53 |
| [[bld_config_constraint_spec]] | sibling | 0.53 |
