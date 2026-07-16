---
kind: config
id: bld_config_chain
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: inline
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: pillar
quality: null
title: "Config Chain"
version: "1.0.0"
author: n03_builder
tags: [chain, builder, examples]
tldr: "Golden and anti-examples for chain construction, demonstrating ideal structure and common pitfalls."
domain: "chain construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, chain construction, config chain, chain, builder, examples, "p03_ch_{pipeline_slug}.md"]
density_score: 0.90
related:
  - bld_instruction_chain
  - bld_schema_chain
  - chain-builder
  - p01_kc_chain
  - p10_lr_chain_builder
---
# Config: chain Production Rules
## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p03_ch_{pipeline_slug}.md` | `p03_ch_research_to_kc.md` |
| Builder directory | kebab-case | `chain-builder/` |
| Frontmatter fields | snake_case | `steps_count`, `error_strategy` |
| Pipeline slug | snake_case, lowercase | `research_to_kc`, `content_enrichment` |
Rule: id MUST equal filename stem.
## File Paths
- Output: `cex/P03_prompt/examples/p03_ch_{pipeline_slug}.md`
- Compiled: `cex/P03_prompt/compiled/p03_ch_{pipeline_slug}.yaml`
## Size Limits (aligned with SCHEMA)
- Body: max 6144 bytes
- Total (frontmatter + body): ~8000 bytes
- Density: >= 0.80
## Flow Type Enum
| Value | When to use | Example |
|-------|-------------|---------|
| sequential | Steps run in order A->B->C | Most pipelines |
| branching | Steps branch based on condition | Intent-based routing |
| parallel | Steps run simultaneously, merge results | Multi-perspective analysis |
| mixed | Combination of above patterns | Complex pipelines |
## Error Strategy Enum
| Value | When to use | Example |
|-------|-------------|---------|
| fail_fast | Stop chain on first failure | Critical data paths |
| skip | Skip failed step, continue with partial data | Enrichment/optional steps |
| retry | Retry failed step N times before failing | Transient API errors |
| fallback | Use alternative step on failure | Graceful degradation |
## Body Requirements
- Purpose: 2-4 sentences, must explain the transformation
- Steps: numbered, each with Input/Prompt/Output subsections
- Data Flow: ASCII diagram showing step connections
- Error Handling: strategy + failure behavior

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_chain]] | upstream | 0.40 |
| [[bld_schema_chain]] | upstream | 0.40 |
| [[chain-builder]] | upstream | 0.36 |
| [[p01_kc_chain]] | upstream | 0.36 |
| [[p10_lr_chain_builder]] | downstream | 0.34 |
