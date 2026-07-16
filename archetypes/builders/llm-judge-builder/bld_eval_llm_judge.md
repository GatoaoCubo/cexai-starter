---
kind: quality_gate
id: p11_qg_llm_judge
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of llm_judge artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: llm_judge"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, llm-judge, P07, evals, criteria, scale, few-shot]
tldr: "Pass/fail gate for llm_judge artifacts: judge_model presence, criteria completeness, scale anchors, few-shot calibration, and boundary compliance."
domain: "LLM-as-Judge configuration — automated quality evaluators with declared model, criteria, scale, and calibration examples"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [llm-as-judge configuration, and calibration examples, judge_model presence, criteria completeness, scale anchors, few-shot calibration, and boundary compliance]
density_score: 0.90
related:
  - llm-judge-builder
---
## Quality Gate

# Gate: llm_judge
## Definition
| Field | Value |
|---|---|
| metric | llm_judge artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: llm_judge` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p07_judge_[a-z][a-z0-9_]+$` | ID contains uppercase, spaces, hyphens, or wrong prefix |
| H03 | ID equals filename stem | `id: p07_judge_foo` but file is `p07_judge_bar.md` |
| H04 | Kind equals literal `llm_judge` | `kind: scorer` or `kind: rubric` or any other value |
| H05 | Quality field is null | `quality: 7.5` or any non-null value |
| H06 | All required fields present | Missing `judge_model`, `criteria`, or `scale` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Criteria independence | 1.0 | Each criterion measures exactly one quality aspect; no overlap between criteria |
| Scale anchor quality | 1.0 | Anchors define concrete observable behaviors, not vague labels like "good" or "bad" |
| Few-shot coverage | 1.0 | At least 2 examples present; covers both high and low score ends of scale |
| Few-shot rationale quality | 1.0 | Each example has chain-of-thought rationale explaining score assignment |
| Judge model apownteness | 0.5 | Model is from different family than likely evaluated model (reduces self-enhancement bias) |
| Framework mapping | 0.5 | Framework field set and integration pattern documented |
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
| conditions | Experimental judge under active calibration — few-shot examples not yet finalized |
| approver | Author self-certification with calibration plan and deadline |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 7d — experimental judges must reach >= 7.0 or be removed |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H07 (missing judge_model means the artifact is a scoring_rubric, not a judge) |

## Examples

# Examples: llm-judge-builder
## Golden Example
INPUT: "Create an LLM judge to evaluate RAG responses for faithfulness and answer relevance using DeepEval"
OUTPUT:
```yaml
id: p07_judge_rag_quality
kind: llm_judge
pillar: P07
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "RAG Response Quality Judge"
```
## Overview
Evaluates RAG pipeline outputs on faithfulness (claims supported by retrieved context) and answer relevance (response addresses the user question). Reference-based judge — requires input question and retrieved context.
## Criteria
### faithfulness
Every factual claim must be traceable to context. High (5): all claims supported. Low (1): key claims hallucinated.
### answer_relevance
Output must directly address the question. High (5): fully addresses with no off-topic content. Low (1): fails to address or entirely off-topic.
## Scale
Type: likert | Range: 1-5 | 1=Failing, 3=Acceptable, 5=Excellent

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p07_judge_ pattern (H02 pass)
- kind: llm_judge (H04 pass)
- judge_model is concrete identifier "gpt-4o" (H07 pass)

## Anti-Example
INPUT: "Create a judge to score responses"
BAD OUTPUT:
```yaml
id: response-scorer
kind: scorer
criteria: [quality]
scale: 1-10
judge_model: ""
quality: 8.5
tags: [eval]
```
Scores responses on quality.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
