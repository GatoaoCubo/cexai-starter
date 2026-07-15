---
kind: quality_gate
id: p11_qg_enum_def
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of enum_def artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: enum_def"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, enum-def, P06, enumeration, finite-values, schema]
tldr: "Pass/fail gate for enum_def artifacts: value completeness, per-value descriptions, extensibility declaration, and framework representation accuracy."
domain: "enumeration definition — finite named value sets with per-value descriptions and framework representations"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [enumeration definition, value completeness, per-value descriptions, extensibility declaration, and framework representation accuracy, quality-gate, enum-def]
density_score: 0.90
related:
  - bld_knowledge_card_enum_def
  - p11_qg_quality_gate
  - bld_instruction_enum_def
  - p11_qg_cli_tool
  - enum-def-builder
---
## Quality Gate

# Gate: enum_def
## Definition
| Field | Value |
|---|---|
| metric | enum_def artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: enum_def` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p06_enum_[a-z][a-z0-9_]+$` | ID contains uppercase, spaces, hyphens, or missing prefix |
| H03 | ID equals filename stem | `id: p06_enum_status` but file is `p06_enum_state.md` |
| H04 | Kind equals literal `enum_def` | `kind: type_def` or `kind: schema` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `values`, `name`, `version`, `tldr`, or `tags` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Value coverage | 1.0 | All meaningful domain values represented; no obvious omissions |
| Per-value descriptions | 1.0 | Each value has a clear description explaining meaning and when to use |
| Extensibility declaration | 1.0 | extensible field present and accurate for the domain |
| Default documentation | 0.5 | Default value documented if the field has a natural default |
| Deprecation clarity | 0.5 | Deprecated values listed with reason; migration path noted |
| Framework representations | 1.0 | Usage section covers at least JSON Schema + one of: Pydantic, Zod, TypeScript |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Internal scratch enum used only during development, never referenced by other artifacts |
| approver | Author self-certification with comment explaining transient scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — scratch enums must be promoted to >= 7.0 or removed |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H07 (single-value enum is a constant — wrong kind) |

## Examples

# Examples: enum-def-builder
## Golden Example
INPUT: "Create enum for CEX artifact publication status"
OUTPUT:
```yaml
id: p06_enum_publication_status
kind: enum_def
pillar: P06
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "Publication Status"
```
## Overview
Lifecycle states for CEX artifacts progressing from authoring through archival. Used by pool indexers, quality gate runners, and routing systems to filter by readiness.
## Values
### draft
Initial state. Artifact is being authored. Quality gates not run. Not visible in pool.
### review
Submitted for quality gate evaluation. No edits permitted until review complete.
### published
Passed all HARD gates and met score threshold. Available in pool for routing.
### deprecated
Superseded by newer version. Retained for backward compatibility; do not route new requests here.
### archived
Removed from active routing. Preserved for historical reference and audit trail only.
## Usage
JSON Schema: `{"enum": ["draft", "review", "published", "deprecated", "archived"]}`
Pydantic: `class PublicationStatus(str, Enum): DRAFT = "draft"`
Zod: `z.enum(["draft", "review", "published", "deprecated", "archived"])`
TypeScript: `type PublicationStatus = "draft" | "review" | "published" | "deprecated" | "archived";`
## Constraints
Default: draft. Extensible: no. Deprecated: none.

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p06_enum_ pattern (H02 pass)
- kind: enum_def (H04 pass)
- values list matches ## Values section names exactly (H08 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
