---
kind: quality_gate
id: p11_qg_eval_dataset
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of eval_dataset artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: eval_dataset"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, eval-dataset, P07, evals, splits, schema-fields]
tldr: "Pass/fail gate for eval_dataset artifacts: schema completeness, split integrity, size declaration, and framework integration."
domain: "evaluation dataset — curated test case collections with declared schema, splits, and framework integration"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [evaluation dataset, and framework integration, schema completeness, split integrity, size declaration, quality-gate, eval-dataset]
density_score: 0.90
related:
  - p11_qg_cli_tool
  - p11_qg_quality_gate
  - eval-dataset-builder
  - p11_qg_enum_def
  - p11_qg_validator
---
## Quality Gate

# Gate: eval_dataset
## Definition
| Field | Value |
|---|---|
| metric | eval_dataset artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: eval_dataset` |

## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p07_ds_[a-z][a-z0-9_]+$` | ID missing prefix, contains uppercase, spaces, or invalid chars |
| H03 | ID equals filename stem | `id: p07_ds_foo` but file is `p07_ds_bar.md` |
| H04 | Kind equals literal `eval_dataset` | `kind: dataset` or `kind: golden_test` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `size`, `splits`, `schema_fields`, `name`, or `version` |

## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Schema completeness | 1.0 | All schema_fields documented in ## Schema section with type and description |
| Split rationale | 1.0 | Each split has explicit rationale; eval-only datasets document why train is 0 |
| Framework integration | 1.0 | Loading pattern documented for target framework with code example |
| Source declaration | 1.0 | Data origin (human/synthetic/scraped/adversarial) declared with quality implication |
| Size credibility | 0.5 | Size is realistic for stated task type; growth strategy mentioned |
| Versioning strategy | 1.0 | Semver rules defined; schema migration path described for breaking changes |

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
| conditions | Prototype dataset used only during local development, never shared or used in CI |
| approver | Author self-certification with comment explaining prototype-only scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — prototype datasets must be promoted to >= 7.0 or removed from repo |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H08 (split math errors cause silent data leakage) |

## Examples

# Examples: eval-dataset-builder
## Golden Example
INPUT: "Create eval dataset for testing CEX artifact quality gate validation — 200 cases covering all 10 HARD gate checks"
OUTPUT:
```yaml
id: p07_ds_artifact_quality_gate_eval
kind: eval_dataset
pillar: P07
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "CEX Artifact Quality Gate Evaluation Dataset"
```
## Overview
Tests the CEX artifact quality gate validator across all 10 HARD gate conditions. Used by builder_agent to verify validation logic and by CI to catch regression in gate checks.
## Schema
### input
Type: dict. The artifact under evaluation — `frontmatter` (dict) and `body` (string).
Example: `{"frontmatter": {"id": "p04_cli_foo", "kind": "cli_tool", "quality": null}, "body": "## Commands\n..."}`
### expected_output
Type: dict. Expected gate result — `passed` (bool), `failures` (list[string]), `score` (float or null).
Example: `{"passed": false, "failures": ["H05: quality is not null"], "score": null}`
### metadata
Type: dict. Case-level annotations for filtering and analysis.
Values: `{gate_id: "H05", failure_mode: "quality_not_null", difficulty: "easy", artifact_kind: "cli_tool"}`
## Splits
| Split | Percentage | Cases |
|-------|-----------|-------|
| test | 100% | 200 |

Pure evaluation — no training use for a rule-based validator. All cases are test-only.
## Integration
Framework: braintrust. Loading: `project.datasets.create(name="p07_ds_artifact_quality_gate_eval")` — iterate cases, call `validate_artifact(case["input"]["frontmatter"], case["input"]["body"])`, compare to `case["expected"]`.

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p07_ds_ pattern (H02 pass)
- kind: eval_dataset (H04 pass)
- schema_fields has input + expected_output (H07 pass)
## Anti-Example
INPUT: "Create eval dataset for testing my chatbot"
BAD OUTPUT:
```yaml
id: chatbot-eval
kind: dataset
pillar: evals
name: My Chatbot Eval
size: "a lot"
quality: 8.5
tags: [eval]
```
Some test cases for my chatbot.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
