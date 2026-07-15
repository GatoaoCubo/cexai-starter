---
id: p01_kc_reward_signal
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P01
subject_pillar: P11
title: "Reward Signal: Continuous Scalar Feedback for Optimizers and Gates"
version: 1.0.0
created: 2026-03-30
updated: 2026-03-30
author: research_agent
domain: reward_signal
quality: null
tags: [reward_signal, P11, GOVERN, kind-kc]
tldr: "Continuous scalar score (0–10) emitted after agent actions to drive optimizer feedback and learning record promotion"
when_to_use: "Building, reviewing, or reasoning about reward_signal artifacts"
keywords: [score, feedback, reinforcement]
feeds_kinds: [reward_signal]
density_score: null
related:
  - p01_kc_llm_judge
  - bld_collaboration_llm_judge
  - p07_llm_judge
  - llm-judge-builder
  - bld_knowledge_card_reward_signal
---

# Reward Signal

## Spec
```yaml
kind: reward_signal
pillar: P11
llm_function: GOVERN
max_bytes: 2048
naming: p11_reward.md
core: true
```

## What It Is
A reward signal is a continuous scalar score (0.0–10.0) emitted after an agent action or output, used to drive optimizer tuning, quality gate decisions, and learning record promotion. It is a feedback signal, not a barrier — a score of 6.0 does not block execution but informs the optimizer. It is NOT quality_gate (binary pass/fail enforcer; reward_signal is continuous input to gates and optimizers).

## Cross-Framework Map
| Framework/Provider | Class/Concept | Notes |
|-------------------|---------------|-------|
| LangChain | LangSmith `EvaluationResult.score` | Traces carry numeric scores from evaluator runs |
| LlamaIndex | `SemanticSimilarityEvaluator` score | Returns float similarity; used as reward signal for RAG quality |
| CrewAI | Task output quality numeric assessment | Custom scorer on `TaskOutput.raw`; no native scalar reward |
| DSPy | `SemanticF1`, `answer_exact_match` | DSPy metrics return float [0,1]; scale to [0,10] for CEX |
| Haystack | Custom evaluation component score output | Score component outputs float; wire to optimizer component |
| OpenAI | Evals API `score` field | Graders emit numeric scores per sample |
| Anthropic | Custom LLM-judge score | Prompt claude-haiku to score output 0–10; low latency scorer |

## Key Parameters
| Parameter | Type | Default | Tradeoff |
|-----------|------|---------|----------|
| scale | string | 0-10 | 0-10 (CEX standard); 0-1 for DSPy interop (multiply by 10) |
| scorer_type | enum | llm-judge | llm-judge/heuristic/human — llm-judge: balanced; human: highest quality |
| emit_on | enum | task_complete | task_complete/batch_complete/session_end |
| dimensions | list | [quality] | Multi-dimensional: [quality, relevance, density, accuracy] |

## Patterns
| Pattern | When to Use | Example |
|---------|-------------|---------|
| Multi-dimensional score | Complex outputs needing breakdown | `{quality: 8.2, relevance: 7.5, density: 9.0}` → weighted average |
| Fast heuristic pre-score | High-throughput pipelines | Regex/length heuristics filter obvious fails before LLM judge |
| Human-in-loop calibration | Initial optimizer setup | Sample 50 outputs; human scores calibrate LLM judge |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Binary score (0 or 10 only) | No gradient for optimizer; equivalent to quality gate | Use continuous [0,10]; reserve 0 and 10 for obvious extremes |
| Scoring without dimensions | Single score masks component failure | Score at least quality + relevance separately |
| LLM judge scoring LLM outputs on same call | Self-serving bias; inflated scores | Use separate smaller model as judge (claude-haiku vs sonnet output) |

## Integration Graph
```
[action_prompt] --> [reward_signal] --> [optimizer]
                         |         --> [quality_gate]
                         |         --> [learning_record]
```

## Decision Tree

| Score band | Action |
|------------|--------|
| >= 9.5 | promote to golden pool + write learning_record |
| 8.0-9.4 | promote to pool; feed optimizer as a positive example |
| 7.0-7.9 | experimental; optimizer uses as a weak positive |
| < 7.0 | optimizer uses as a negative example; check quality_gate on_fail |
| default | emit on every task_complete; never skip scoring |

## Quality Criteria
- GOOD: Has scorer_type, scale, emit_on, dimensions; score is float [0,10]
- GREAT: Multi-dimensional with weighted average; calibrated against human baseline; fast pre-filter
- FAIL: Binary only; no dimensions; same model judges its own output; score never actually used downstream

## How to use

```text
ROLE: you are wiring continuous feedback into an optimizer or quality gate.
1. Set scale (0-10 CEX standard), scorer_type, emit_on, and at least two dimensions.
2. Emit the signal after each task_complete; route it to optimizer + gate + learning_record.
3. Apply the Decision Tree thresholds to decide promotion vs negative-example usage.
4. Avoid the Anti-Patterns: never binary-only, never let a model judge its own output.
Primary 8F verb: GOVERN (the reward_signal feeds F7 scoring; it informs, it does not block).
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_llm_judge]] | sibling | 0.35 |
| [[bld_collaboration_llm_judge]] | downstream | 0.34 |
| p07_llm_judge | upstream | 0.32 |
| [[llm-judge-builder]] | upstream | 0.30 |
| [[bld_knowledge_card_reward_signal]] | sibling | 0.29 |
