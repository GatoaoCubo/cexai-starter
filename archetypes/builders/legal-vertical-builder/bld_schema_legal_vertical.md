---
kind: schema
id: bld_schema_legal_vertical
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for legal_vertical
quality: null
title: "Schema Legal Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [legal_vertical, builder, schema]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for legal_vertical"
domain: "legal_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [legal_vertical construction, schema legal vertical, legal_vertical, builder, schema, frontmatter fields, body structure, jurisdictional scope, compliance requirements, legal framework]
density_score: 0.85
related:
  - bld_schema_usage_report
  - bld_schema_pitch_deck
  - bld_schema_benchmark_suite
  - bld_schema_reranker_config
  - bld_schema_playground_config
---

## Frontmatter Fields
### Required
| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| id | string | yes |  | Must match ID Pattern |
| kind | string | yes |  | Always "legal_vertical" |
| pillar | string | yes |  | Always "P01" |
| title | string | yes |  | Legal document title |
| version | string | yes | "1.0" | Semantic versioning |
| created | datetime | yes |  | ISO 8601 format |
| updated | datetime | yes |  | ISO 8601 format |
| author | string | yes |  | Legal entity or individual |
| domain | string | yes |  | Jurisdiction or regulatory area |
| quality | null | yes | null | Never self-score; peer review assigns |
| tags | list | yes | [] | Keywords for classification |
| tldr | string | yes |  | Summary of legal implications |
| jurisdiction | string | yes |  | Governing legal territory |
| compliance_status | string | yes |  | "pending", "approved", "revoked" |

### Recommended
| Field | Type | Notes |
|---|---|---|
| legal_framework | string | Reference to governing laws |
| regulatory_body | string | Authority overseeing document |

## ID Pattern
^p01_lv_[a-z][a-z0-9_]+.md$

## Body Structure
1. **Overview**
   Summary of legal vertical's purpose and scope.

2. **Jurisdictional Scope**
   Detailed description of applicable regions/laws.

3. **Compliance Requirements**
   Mandatory obligations for stakeholders.

4. **Legal Framework**
   References to statutes, regulations, or treaties.

5. **Regulatory Bodies**
   Entities responsible for enforcement and oversight.

6. **Amendment History**
   Log of revisions with dates and rationale.

## Constraints
- Jurisdiction must align with domain-specific field values.
- All legal terms must use official terminology from governing bodies.
- Quality field must be assigned by peer review, not self-assigned.
- Version numbers must follow semantic versioning (e.g., 1.0.0).
- Tags must include at least one keyword from predefined legal taxonomies.
- Files exceeding 6144 bytes must be split into multiple documents.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_usage_report]] | sibling | 0.63 |
| [[bld_schema_pitch_deck]] | sibling | 0.63 |
| [[bld_schema_benchmark_suite]] | sibling | 0.62 |
| [[bld_schema_reranker_config]] | sibling | 0.62 |
| [[bld_schema_playground_config]] | sibling | 0.60 |
