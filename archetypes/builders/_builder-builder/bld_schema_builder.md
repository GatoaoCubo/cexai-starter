---
kind: schema
id: bld_schema_builder
pillar: P06
llm_function: CONSTRAIN
purpose: Field definitions and constraints for builder artifacts
quality: null
title: "Schema Builder"
version: "1.0.0"
author: n03_builder
tags: [_builder, builder, examples]
tldr: "Golden and anti-examples for _builder construction, demonstrating ideal structure and common pitfalls."
domain: "_builder construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [builder construction, schema builder, builder, examples, frontmatter fields, universal fields, size constraints, related artifacts, config enum, sibling]
density_score: 0.90
related:
  - bld_schema_pitch_deck
  - bld_schema_usage_report
  - bld_schema_reranker_config
  - bld_schema_quickstart_guide
  - bld_schema_dataset_card
---
# Schema: _builder-builder

## Frontmatter Fields (per generated ISO)
| Field | Type | Required | Constraint |
|-------|------|----------|------------|
| id | string | yes | Must equal filename stem |
| kind | string | yes | Must match target kind |
| pillar | string | yes | P01-P12 |
| llm_function | enum | yes | CONSTRAIN/BECOME/INJECT/REASON/CALL/PRODUCE/GOVERN/COLLABORATE |
| purpose | string | yes | One-line description |

## Universal Fields (added by hydration)
| Field | ISO | Type | Default |
|-------|-----|------|---------|
| keywords | manifest | list[str] | 4-8 terms |
| triggers | manifest | list[str] | 2-4 phrases |
| capabilities | manifest | string | 3 layers L1/L2/L3 |
| memory_scope | memory | enum | project |
| observation_types | memory | list | [user,feedback,project,reference] |
| effort | config | enum | medium |
| max_turns | config | int | 25 |
| disallowed_tools | config | list | [] |
| hooks | config | map | {nulls} |
| permission_scope | config | enum | nucleus |

## Size Constraints
1. Standard ISO: max 4096 bytes
2. Instruction ISO: max 6144 bytes
3. Total builder: 13 files, < 60KB aggregate

## Metadata

```yaml
id: bld_schema_builder
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-schema-builder.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_pitch_deck]] | sibling | 0.40 |
| [[bld_schema_usage_report]] | sibling | 0.40 |
| [[bld_schema_reranker_config]] | sibling | 0.39 |
| [[bld_schema_quickstart_guide]] | sibling | 0.39 |
| [[bld_schema_dataset_card]] | sibling | 0.38 |
