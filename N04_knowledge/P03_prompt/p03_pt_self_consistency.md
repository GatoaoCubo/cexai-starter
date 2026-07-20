---
id: p03_pt_self_consistency
kind: prompt_technique
pillar: P03
title: "Self-Consistency Sampling"
version: "1.0"
created: "2026-06-03"
updated: "2026-06-03"
author: n04_knowledge
domain: prompt_engineering
quality: null
technique_type: ensemble-sampling
difficulty_level: intermediate
tags: [self-consistency, chain-of-thought, ensemble, variance-reduction, reasoning, P03]
tldr: "Sample k independent CoT paths, aggregate by majority vote to reduce single-sample variance on high-stakes reasoning tasks."
example_use_case: "Solve a math word problem: generate 5 independent CoT solutions, pick the most frequent answer."
source: "github.com/dair-ai/Prompt-Engineering-Guide"
source_author: "DAIR.AI"
source_license: "MIT"
related:
  - prompt_technique_react
  - p01_kc_repo_assimilation_candidates
  - bld_schema_prompt_technique
  - kc_reasoning_strategy
---

## Overview

Self-Consistency (Wang et al., 2022) decouples _generation_ from _selection_.
Sample k independent CoT completions at temperature > 0, then return the answer
that appears most often across the k paths.

Core insight: for reasoning tasks the correct answer is reachable via multiple
paths; aggregation removes the noise introduced by any single greedy path.

**Scaffold:** (1) compose CoT prompt, (2) sample k completions (temp ~0.7),
(3) extract final answer token from each, (4) majority-vote.

## Application Context

| Condition | Use? |
|-----------|------|
| High-stakes arithmetic / logic (single sample unreliable) | YES |
| Complex multi-step reasoning: math, commonsense, legal | YES |
| Tasks with extractable answer token (numeric, classification) | YES |
| Open-ended generation (story, summary) | NO -- no vote applicable |
| Latency/token-constrained pipeline | CAUTION -- cost = k x tokens |

Cost tradeoff: k=5 costs 5x tokens/latency. Diminishing returns plateau ~k=10-20.
k=5 is the production sweet spot for most tasks.

## Example

Task: "Janet has 15 apples, gives 4 to her brother, buys 7 more. Total?"

- Path A: 15-4=11, 11+7=18. Answer: 18
- Path B: 15, lose 4 (11), gain 7 (18). Answer: 18
- Path C: 15+7=22, 22-4=18. Answer: 18

Vote 3/3: **18**. One arithmetic slip on any single path would not change the winner.

## Best Practices

1. Set temp 0.6-0.8. Temp 0 collapses all k samples into identical paths.
2. Add a "Final answer:" suffix so extraction is deterministic.
3. Log all k paths -- high answer divergence = low confidence signal.
4. Combine with few-shot CoT examples to improve path diversity quality.
5. k=20 offline experiments reveal the knee; ship k=5 in production.

## CEXAI Mapping

Self-Consistency is the backbone of **F7c COUNCIL** (8f-reasoning.md):

| Self-Consistency concept | CEXAI F7c equivalent |
|--------------------------|-------------------|
| k sampled paths | N independent judge evaluations |
| Majority vote | consensus_score (mean of N) |
| Answer variance | divergence_score (stddev) |
| High divergence flag | block-publication gate (>0.3) |
| Single dissenting path | surfaced dissent rationale (never suppressed) |

Related kinds: `llm_judge` (P07) = single judge instance; `crew_template` (P12)
with `process: consensus` = judge pool assembly; `scoring_rubric` (P07) =
answer-extraction layer each judge applies.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[prompt_technique_react]] | sibling | 0.72 |
| [[p01_kc_repo_assimilation_candidates]] | upstream | 0.65 |
| [[bld_schema_prompt_technique]] | downstream | 0.50 |
| [[kc_reasoning_strategy]] | sibling | 0.48 |
