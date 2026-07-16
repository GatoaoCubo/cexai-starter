---
kind: schema
id: bld_schema_contributor_guide
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for contributor_guide
quality: null
title: "Schema Contributor Guide"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [contributor_guide, builder, schema]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for contributor_guide"
domain: "contributor_guide construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [contributor_guide construction, schema contributor guide, contributor_guide, builder, schema, quality, frontmatter fields, body structure, contribution workflow, getting started]
density_score: 0.85
related:
  - bld_schema_integration_guide
  - bld_schema_reranker_config
  - bld_schema_benchmark_suite
  - bld_schema_pitch_deck
  - bld_schema_quickstart_guide
---

## Frontmatter Fields
### Required
| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| id | string | yes | null | Must match ID Pattern |
| kind | string | yes | "contributor_guide" | Fixed value |
| pillar | string | yes | "P05" | Fixed value |
| title | string | yes | null | Descriptive title |
| version | string | yes | "1.0" | Semantic versioning |
| created | datetime | yes | null | ISO 8601 format |
| updated | datetime | yes | null | ISO 8601 format |
| author | string | yes | null | Maintainer name |
| domain | string | yes | null | e.g., "engineering" |
| quality | null | yes | null | Never self-score; peer review assigns |
| tags | list | yes | [] | Keywords for search |
| tldr | string | yes | null | Summary of guide |
| contribution_types | list | yes | [] | e.g., ["code", "docs"] |
| onboarding_steps | list | yes | [] | e.g., ["fork repo", "setup env"] |

### Recommended
| Field | Type | Notes |
|---|---|---|
| review_process | string | Describe peer review workflow |
| example_contributions | list | Sample pull requests/issues |

## ID Pattern
^p05_cg_[a-z][a-z0-9_]+.md$

## Body Structure
1. **Introduction**
   - Purpose of the guide
   - Scope and audience

2. **Contribution Workflow**
   - Step-by-step process for submitting changes

3. **Code of Conduct**
   - Behavioral expectations and enforcement

4. **Getting Started**
   - Setup instructions, tools, and prerequisites

5. **Submission Guidelines**
   - Formatting, testing, and documentation standards

6. **Review Process**
   - How contributions are evaluated and merged

## Constraints
- Enforce ID pattern strictly (regex must match exactly)
- Use ASCII-only characters (no Unicode)
- Keep total markdown lines under 80
- No frontmatter in final file
- Ensure `quality` field is peer-reviewed, not self-assigned
- File size must not exceed 6144 bytes (6KB)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_integration_guide]] | sibling | 0.69 |
| [[bld_schema_reranker_config]] | sibling | 0.68 |
| [[bld_schema_benchmark_suite]] | sibling | 0.65 |
| [[bld_schema_pitch_deck]] | sibling | 0.64 |
| [[bld_schema_quickstart_guide]] | sibling | 0.63 |
