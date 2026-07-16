---
kind: schema
id: bld_schema_model_registry
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for model_registry
quality: null
title: "Schema Model Registry"
version: "1.0.0"
author: wave1_builder_gen
tags: [model_registry, builder, schema]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for model_registry"
domain: "model_registry construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [model_registry construction, schema model registry, model_registry, builder, schema, frontmatter fields, related artifacts, sibling, notes, version]
density_score: 0.85
related:
  - bld_schema_experiment_tracker
  - bld_schema_training_method
  - bld_schema_dataset_card
  - bld_schema_model_architecture
  - bld_schema_multimodal_prompt
---
## Frontmatter Fields
### Required
| Field | Type | Required | Default | Notes |
| :--- | :--- | :--- | :--- | :--- |
| id | string | Y | N/A | Unique identifier |
| kind | string | Y | model_registry | CEX type |
| pillar | string | Y | P10 | Organizational pillar |
| title | string | Y | N/A | Descriptive name |
| version | string | Y | 1.0.0 | Semantic version |
| created | datetime | Y | N/A | Creation timestamp |
| updated | datetime | Y | N/A | Last modification |
| author | string | Y | N/A | Document owner |
| domain | string | Y | N/A | Functional domain |
| quality | string | Y | N/A | Reliability score |
| tags | list | Y | [] | Metadata tags |
| tldr | string | Y | N/A | Brief summary |
| model_type | string | Y | N/A | e.g., LLM, CNN |
| framework | string | Y | N/A | e.g., PyTorch, JAX |

### Recommended
| Field | Type | Required | Default | Notes |
| :--- | :--- | :--- | :--- | :--- |
| base_model | string | N | N/A | Foundation model ref |
| training_data | string | N | N/A | Dataset lineage link |
| metrics | object | N | N/A | Accuracy/Latency |
| status | string | N | N/A | e.g., Production |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_experiment_tracker]] | sibling | 0.59 |
| [[bld_schema_training_method]] | sibling | 0.47 |
| [[bld_schema_dataset_card]] | sibling | 0.47 |
| [[bld_schema_model_architecture]] | sibling | 0.46 |
| [[bld_schema_multimodal_prompt]] | sibling | 0.44 |
