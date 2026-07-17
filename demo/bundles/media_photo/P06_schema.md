---
kind: schema
id: bld_schema_multimodal_prompt
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for multimodal_prompt
quality: null
title: "Schema Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, schema]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for multimodal_prompt"
domain: "multimodal_prompt construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [multimodal_prompt construction, schema multimodal prompt, multimodal_prompt, builder, schema, frontmatter fields, body structure, prompt structure, example usage, related artifacts]
density_score: 0.85
related:
  - bld_schema_benchmark_suite
  - bld_schema_reranker_config
  - bld_schema_integration_guide
  - bld_schema_app_directory_entry
  - bld_schema_eval_metric
---

## Frontmatter Fields
### Required
| Field     | Type             | Required | Default | Notes                              |
|-----------|------------------|----------|---------|------------------------------------|
| id        | string           | yes      | null    | Unique identifier                  |
| kind      | string           | yes      | null    | Must be "multimodal_prompt"        |
| pillar    | string           | yes      | null    | P03                                |
| title     | string           | yes      | null    | Descriptive title                  |
| version   | string           | yes      | "1.0"   | Version control                    |
| created   | datetime         | yes      | null    | ISO 8601                           |
| updated   | datetime         | yes      | null    | ISO 8601                           |
| author    | string           | yes      | null    | Author name                        |
| domain    | string           | yes      | null    | Application domain                 |
| quality   | null             | yes      | null    | Never self-score; peer review assigns |
| tags      | array<string>    | yes      | []      | Keywords                           |
| tldr      | string           | yes      | null    | One-sentence summary               |
| modalities | array<string>   | yes      | null    | Supported modalities (e.g., text, image) |
| prompt_type | string        | yes      | null    | Type (e.g., instruction, query)    |

### Recommended
| Field           | Type             | Notes                          |
|------------------|------------------|--------------------------------|
| license          | string           | Open-source license            |
| source           | string           | Original source                |
| related_works    | array<string>    | Cited works                    |
| validation_metrics | array<string> | Evaluation criteria            |

## ID Pattern
^p03_mmp_[a-z][a-z0-9_]+.md$

## Body Structure
1. **Introduction**: Purpose and scope of the prompt.
2. **Modalities**: Detailed description of supported input/output types.
3. **Prompt Structure**: Syntax, formatting rules, and examples.
4. **Example Usage**: Real-world application scenarios.
5. **Validation**: Metrics and peer review process.

## Constraints
- ID must match ^p03_mmp_[a-z][a-z0-9_]+.md$
- Total size <= 4096 bytes
- All required fields must be present
- Quality field is peer-reviewed only
- ASCII-only characters required
- <= 80 lines total

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_benchmark_suite | sibling | 0.67 |
| bld_schema_reranker_config | sibling | 0.66 |
| bld_schema_integration_guide | sibling | 0.66 |
| bld_schema_app_directory_entry | sibling | 0.64 |
| [[bld_schema_eval_metric]] | sibling | 0.64 |
