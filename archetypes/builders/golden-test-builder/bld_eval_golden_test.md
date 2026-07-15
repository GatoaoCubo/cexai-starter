---
kind: quality_gate
id: p11_qg_golden_test
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of golden_test artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: golden_test"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, golden-test, calibration, evaluation, quality-baseline, P11]
tldr: "Validates golden_test artifacts: verified 9.5+ source quality, rationale-to-gate mapping, and non-self-referential target kind."
domain: "golden_test — reference quality calibration cases scoring 9.5+ with rationale mapped to evaluation gates"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [validates golden_test artifacts, source quality, rationale-to-gate mapping, and non-self-referential target kind, quality-gate, golden-test, calibration]
density_score: 0.93
related:
  - p11_qg_few_shot_example
  - golden-test-builder
  - p11_qg_quality_gate
  - p11_qg_knowledge_card
  - bld_instruction_golden_test
---
## Quality Gate

# Gate: golden_test
## Definition
| Field     | Value |
|-----------|-------|
| metric    | composite score across SOFT dimensions |
| threshold | >= 7.0 to publish; >= 9.5 for golden (the golden_test itself must also reach 9.5) |
| operator  | weighted average after all HARD gates pass |
| scope     | all artifacts where `kind: golden_test` |
All HARD gates are AND-logic: one failure rejects the artifact regardless of SOFT score.
## HARD Gates
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Any YAML syntax error |
| H02 | ID matches `^p07_gt_[a-z][a-z0-9_]+$` | Wrong format or namespace |
| H03 | ID equals filename stem (no extension) | Mismatch between id field and file name |
| H04 | Kind equals literal `golden_test` | Any other value |
| H05 | `quality` field is null | Any non-null value |
| H06 | Required fields present: id, kind, pillar, version, created, updated, author, target_kind, quality_threshold, reviewer, domain, quality, tags, tldr | Any missing field |
## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| S01 | `tldr` <= 160 chars, names `target_kind` and what makes this golden | 0.10 | Named=1.0, vague=0.3 |
| S02 | Tags list len >= 3, includes `target_kind` as keyword | 0.06 | Present=1.0, absent=0.0 |
| S03 | Rationale maps to >= 3 distinct gate IDs of `target_kind` | 0.15 | 3+=1.0, 2=0.6, 1=0.3, 0=0.0 |
| S04 | Golden Output is complete and copy-pasteable as a real artifact | 0.14 | Complete=1.0, skeleton=0.4, absent=0.0 |
| S05 | Input Scenario is non-trivial (edge case or high-complexity scenario) | 0.12 | Edge/complex=1.0, trivial=0.3 |
| S06 | Boundary from `few_shot_example` stated (teaches format vs. evaluates quality) | 0.09 | Explicit=1.0, implied=0.4, absent=0.0 |
**Weight sum: 1.00**
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — accepted into calibration set; informs all future scoring for `target_kind` |
| >= 8.0 | PUBLISH — pool-eligible reference; not yet calibration-authoritative |
| >= 7.0 | REVIEW — rationale incomplete or verification source missing |
| < 7.0  | REJECT — redo; likely unverified source quality or missing gate mapping |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Bootstrap only: first golden_test for a brand-new kind where no prior calibration set exists |
| approver | Two independent reviewers must sign off in lieu of automated verification |
| audit trail | Required: both reviewer names, review date, written agreement on quality assessment |

## Examples

# Examples: golden-test-builder
## Golden Example
INPUT: "Create golden test from knowledge_card about prompt caching"
OUTPUT:
```yaml
id: p07_gt_kc_prompt_caching
kind: golden_test
pillar: P07
title: "Golden: KC Prompt Caching"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
target_kind: "knowledge_card"
input: "Destila knowledge about prompt caching for optimize costs LLM"
golden_output_ref: "inline"
quality_threshold: 9.5
rationale: "H01-H10 pass, S01-S18 pass. All HARD gates clear. Density 0.93, actionable, sourced."
edge_case: false
reviewer: "orchestrator"
approval_date: "2026-03-26"
domain: "knowledge"
quality: null
tags: [golden-test, knowledge-card, calibration]
tldr: "Reference KC: prompt caching, density 0.93, all 10 HARD + 18 SOFT gates pass"
density_score: 0.93
linked_artifacts:
  primary: "quality-gate-builder"
  related: [p11_qg_kc_publish]
## Input Scenario
Destila knowledge about prompt caching for optimize costs LLM.
Foco: as funciona, quando usar, economia esperada, limitactions.
## Golden Output
id: p01_kc_prompt_caching
kind: knowledge_card
pillar: P01
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "knowledge-engine"
domain: "llm_optimization"
quality: null
tags: [prompt-caching, cost-optimization, llm, anthropic]
tldr: "Prompt caching reuses prefixes across API calls, cutting costs 90% and latency 85%"
density_score: 0.93
## Conceitos
- Prompt caching stores computed prefixes server-side for reuse
- Minimum cacheable prefix: 1024 tokens (Anthropic), 128 tokens (OpenAI)
- Cache TTL: 5 minutes (Anthropic), session-scoped (OpenAI)
- Write cost: 1.25x base price; read cost: 0.1x base price
## Quando Usar
- System prompts > 1024 tokens repeated across requests
- Few-shot examples reused in batch processing
- Tool definitions shared across conversation turns
- RAG contexts with stable document prefixes
## Economia Esperada
- Anthropic: 90% cost reduction on cached tokens, 85% latency reduction
- OpenAI: 50% cost reduction on cached tokens
- Break-even: 2+ requests with same prefix within TTL window

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
