---
kind: schema
id: bld_schema_experiment_tracker
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for experiment_tracker
quality: null
title: "Schema Experiment Tracker"
version: "1.0.0"
author: wave1_builder_gen
tags: [experiment_tracker, builder, schema]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for experiment_tracker"
domain: "experiment_tracker construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [experiment_tracker construction, schema experiment tracker, experiment_tracker, builder, schema, frontmatter fields, related artifacts, sibling, notes, version]
density_score: 0.85
related:
  - bld_schema_model_registry
  - bld_schema_dataset_card
  - bld_schema_multimodal_prompt
  - bld_schema_training_method
  - bld_schema_benchmark_suite
---
## Frontmatter Fields
### Required
| Field | Type | Required | Default | Notes |
| :---- | :---- | :---: | :---: | :--- |
| id | string | Y | N/A | Unique identifier |
| kind | string | Y | experiment_tracker | Schema type |
| pillar | string | Y | P07 | Pillar designation |
| title | string | Y | N/A | Experiment name |
| version | string | Y | 1.0.0 | Schema version |
| created | datetime | Y | N/A | Creation timestamp |
| updated | datetime | Y | N/A | Last modification |
| author | string | Y | N/A | Document owner |
| domain | string | Y | N/A | Functional area |
| quality | number\|null | Y | null | Peer-review score; null until scored (never self-assign) |
| tags | list | Y | [] | Metadata tags |
| tldr | string | Y | N/A | Executive summary |
| hypothesis | string | Y | N/A | Core assumption |
| metric_primary | string | Y | N/A | Main KPI |

### Recommended
| Field | Type | Notes |
| :---- | :---- | :--- |
| control_group | string | Baseline group definition |
| duration | string | Planned time window |
| confidence_level | float | Statistical significance target |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_model_registry]] | sibling | 0.63 |
| [[bld_schema_dataset_card]] | sibling | 0.48 |
| [[bld_schema_multimodal_prompt]] | sibling | 0.47 |
| [[bld_schema_training_method]] | sibling | 0.46 |
| [[bld_schema_benchmark_suite]] | sibling | 0.44 |
