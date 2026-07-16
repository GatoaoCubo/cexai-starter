---
kind: quality_gate
id: p11_qg_scoring-rubric
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of scoring_rubric artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Scoring Rubric'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: Gates ensuring scoring rubric files define measurable dimensions, justified
  weights summing to 100%, and calibrated tier thresholds.
domain: scoring_rubric
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords: [scoring rubric, scoring-rubric-builder/..., scoring_rubric, quality, quality gate, gates
failure, scoring
dimensions, spec contains, tier thresholds, golden publish]
density_score: 0.85
related:
  - scoring-rubric-builder
  - bld_memory_scoring_rubric
---
## Quality Gate

## Definition
A scoring rubric is an evaluation framework that rates a target artifact on multipland weighted dimensions and maps the aggregate score to an action tier. A rubric passes this gate when a reviewer with no prior context could apply it consistently, two independent reviewers would reach scores within 1.0 point of each other on the same input, and the tier thresholds match established system standards.
## HARD Gates
Failure on any HARD gate = immediate REJECT regardless of score.
| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML with no syntax errors | Unparseable file cannot be indexed or validated |
| H02 | `id` matches the file's directory namespace (`scoring-rubric-builder/...`) | Mismatched IDs cause routing failures |
| H03 | `id` value equals the filename stem (slug portion) | Filename and ID must be the same addressable key |
| H04 | `kind` is exactly `scoring_rubric` (literal match, no variation) | Kind drives the loader; wrong literal silently misroutes |
| H05 | `quality` field is `null` (not filled by author) | Quality is assigned by this gate, not self-reported |
| H06 | All required frontmatter fields present: id, kind, pillar, title, version, created, updated, author, domain, tags, tldr | Incomplete frontmatter breaks downstream consumers |
## SOFT Scoring
Dimensions are weighted; total normalized weight = 100%.
| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | density >= 0.80 (content per token ratio) | 1.0 | Padded with filler prose | Mostly substantive | No filler; every sentence carries information |
| 2 | Each dimension has concrete scale descriptors (what 1, 5, 10 look like) | 1.0 | No descriptors | Endpoint anchors only (1 and 10) | Full anchors at 1, 5, and 10 with examples |
| 3 | Weights justified by utility impact (rationale provided per weight) | 1.0 | No justification | One-sentence generic rationale | Per-dimension rationale tied to artifact utility |
| 4 | Tiers align with standard thresholds (>= 9.5 golden, >= 8.0 publish, >= 7.0 review, < 7.0 reject) | 1.0 | Custom non-standard thresholds | Partially aligned | Exact alignment with system standards |
| 5 | Calibration via golden tests referenced (pointer to 1+ example with known scores) | 0.5 | No calibration reference | Reference named but not accessible | Accessible example with expected score documented |
| 6 | Tags include `scoring-rubric` | 0.5 | Missing | Present but misspelled | Exactly `scoring-rubric` in tags list |

## Examples

# Examples: scoring-rubric-builder
## Golden Example
INPUT: "Create rubric de evaluation 5D para knowledge_cards"
OUTPUT:
```yaml
id: p07_sr_5d_knowledge_card
kind: scoring_rubric
pillar: P07
title: "Rubric: 5D Knowledge Card"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
framework: "5D"
target_kinds: [knowledge_card]
dimensions_count: 5
total_weight: 100
threshold_golden: 9.5
threshold_publish: 8.0
threshold_review: 7.0
automation_status: "semi-automated"
domain: "knowledge"
quality: null
tags: [scoring-rubric, 5d, knowledge-card, evaluation]
tldr: "5-dimension rubric for KCs: density 25%, completeness 25%, actionability 20%, boundary 15%, references 15%"
density_score: 0.92
calibration_set: [p07_gt_kc_prompt_caching]
inter_rater_agreement: 0.85
appeals_process: "Submit to p01-chief with rationale for re-evaluation"
linked_artifacts:
  primary: "quality-gate-builder"
  related: [p11_qg_kc_publish, p07_gt_kc_prompt_caching]
## Framework Overview
5D evaluates knowledge_cards across 5 orthogonal dimensions.
Designed to complement the KC quality_gate (P11) which enforces HARD pass/fail.
This rubric provides the SOFT scoring framework for nuanced quality assessment.
## Dimensions
| Dimension | Weight | Scale | Criteria | Example (10) | Example (5) |
|-----------|--------|-------|----------|-------------|-------------|
| Density | 25% | 0-10 | Ratio of concrete data to total text >= 0.80 | 0.93 density, zero filler phrases | 0.65 density, has "this document describes" |
| Completeness | 25% | 0-10 | All required sections present, >= 3 bullets each | 7 sections, 4+ bullets, all fields filled | 4 sections, some empty, missing tags |
| Actionability | 20% | 0-10 | Contains commands, code, or specific steps | 3 CLI commands, 2 code snippets, concrete steps | General advice, no specific commands |
| Boundary | 15% | 0-10 | Clear IS/IS NOT, no drift to other types | Explicit boundary table, 3+ IS NOT rows | Vague scope, overlaps with other kinds |
| References | 15% | 0-10 | >= 1 source URL, dates, verifiable claims | 3 URLs, all accessible, dated 2026 | No URLs, unverifiable claims |
## Thresholds
| Tier | Score | Action |
|------|-------|--------|
| GOLDEN | >= 9.5 | Promote to calibration set, mark as reference |
| PUBLISH | >= 8.0 | Merge to pool |
| REVIEW | >= 7.0 | Return with specific dimension feedback |
| REJECT | < 7.0 | Redo from scratch with new research |

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_scoring_rubric]] | upstream | 0.46 |
| [[scoring-rubric-builder]] | upstream | 0.43 |
| [[bld_knowledge_scoring_rubric]] | upstream | 0.42 |
| [[kc_scoring_rubric]] | upstream | 0.40 |
| [[bld_memory_scoring_rubric]] | upstream | 0.39 |
