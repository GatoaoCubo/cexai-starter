---
id: p01_kc_llm_judge
kind: knowledge_card
8f: F3_inject
primary_8f: F3_inject
type: kind
pillar: P01
subject_pillar: P07
title: "LLM Judge — Deep Knowledge for llm_judge"
version: 1.0.0
created: 2026-03-30
updated: 2026-03-30
author: knowledge_agent
domain: llm_judge
quality: null
tags: [llm_judge, P07, GOVERN, kind-kc]
tldr: "Configuration for using an LLM as automated evaluator scoring outputs against defined criteria."
when_to_use: "Building, reviewing, or reasoning about llm_judge artifacts"
keywords: [llm-judge, evaluator, automated-eval, scoring, judge_model, scale, chain_of_thought]
long_tails:
  - "how do I score model outputs with another LLM as judge"
  - "how do I calibrate an LLM judge against golden tests"
slots:
  JUDGE_MODEL: "model that grades, e.g. claude-haiku-4-5"
  SCALE: "score range, e.g. 10 or 100"
  CHAIN_OF_THOUGHT: "true to make the verdict interpretable"
  RUBRIC_REF: "scoring_rubric this judge applies"
feeds_kinds: [llm_judge]
density_score: 1.0
linked_artifacts:
  primary: null
  related: []
related:
  - bld_collaboration_llm_judge
  - llm-judge-builder
  - p07_llm_judge
  - n00_judge_config_manifest
  - n00_llm_judge_manifest
---

# LLM Judge

## Spec
```yaml
kind: llm_judge
pillar: P07
llm_function: GOVERN
max_bytes: 2048
naming: p07_judge.md
core: true
```

## What It Is
Configuration for an LLM-as-Judge evaluator: which model to use, what criteria to score, the scale, and the judge system prompt. The judge reads a response and outputs a numeric or categorical score. NOT scoring_rubric—rubric defines WHAT to evaluate; llm_judge defines HOW to evaluate (model, scale, prompt implementation).

## Cross-Framework Map
| Framework/Provider | Class/Concept | Notes |
|---|---|---|
| LangChain | LLMChain as judge | Custom eval chain scoring responses |
| LlamaIndex | LLMRelevancyEvaluator | Built-in LLM-based evaluators |
| CrewAI | Custom judge agent | Dedicated crew agent as evaluator |
| DSPy | LM-based metric | Lambda metric using LM for scoring |
| Haystack | LLMEvaluator | Built-in LLM judge component |
| OpenAI | GPT-4o as judge | Model-graded eval via Evals API |
| Anthropic | Claude as judge | Haiku/Sonnet judge with scoring prompt |

## Key Parameters
| Parameter | Type | Default | Tradeoff |
|---|---|---|---|
| judge_model | str | claude-haiku-4-5 | Stronger = accurate, expensive; weaker = fast |
| scale | int | 10 | 0-5 coarse, 0-100 over-precise |
| chain_of_thought | bool | true | true = interpretable, false = faster |

## Patterns
| Pattern | When to Use | Example |
|---|---|---|
| Pairwise judge | Compare A vs B output quality | "Which is better?" + reason |
| Rubric grader | Score against scoring_rubric criteria | Apply 5D rubric per dimension |
| Calibrated judge | Validate against golden_tests | Tune judge prompt to match human scores |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Using judge as scoring_rubric | Confuses config with criteria | Rubric defines WHAT, judge applies HOW |
| Same model judges own outputs | Self-serving bias | Use different model family for judging |
| No calibration against golden_tests | Unchecked judge drift | Validate judge on >= 10 golden_tests |

## Integration Graph
```
[scoring_rubric] --> [llm_judge] --> [unit_eval score]
[golden_test] -----> [llm_judge calibration]
                          |-------> [benchmark quality metric]
                          |-------> [e2e_eval scoring]
```

## Decision Tree
- IF defining WHAT to evaluate (dimensions, criteria) THEN scoring_rubric
- IF defining HOW to evaluate (model, scale, prompt) THEN llm_judge
- DEFAULT: llm_judge for any automated quality scoring pipeline

## Quality Criteria
- GOOD: judge_model specified, criteria linked to scoring_rubric, scale defined
- GREAT: Calibrated against golden_tests, chain_of_thought enabled, bias mitigation
- FAIL: No rubric link, self-evaluating (same model as target), uncalibrated

### How to use
```text
Role: you are the GOVERN agent at 8F step F7. Load this card BEFORE you author
an llm_judge so HOW you evaluate (model, scale, prompt) is explicit and the
judge does not silently drift.
- Confirm the Spec: kind=llm_judge, pillar P07, GOVERN, max_bytes 2048.
- Pick JUDGE_MODEL from a different model family than the target (avoid self-bias).
- Bind RUBRIC_REF to the scoring_rubric that defines WHAT to score.
- Set SCALE (10 is the default; avoid 0-100 over-precision) and CHAIN_OF_THOUGHT.
- Calibrate against >= 10 golden_tests before trusting the verdict in a pipeline.
```

### Procedure
```text
1. Select JUDGE_MODEL from a family different than the model under test.
2. Link RUBRIC_REF (scoring_rubric) so the criteria are reproducible.
3. Set SCALE and CHAIN_OF_THOUGHT in the judge config.
4. Draft the judge system prompt that emits a score on that scale.
5. Run the judge over >= 10 golden_tests and compare to human scores.
6. Adjust the prompt until judge-vs-human agreement is acceptable.
7. Deploy the calibrated judge into the unit_eval / benchmark pipeline.
```

### Slots
```text
JUDGE_MODEL = <JUDGE_MODEL>            # grader, e.g. claude-haiku-4-5
SCALE       = <SCALE>                  # 10 (default) or 100
CHAIN_OF_THOUGHT = <CHAIN_OF_THOUGHT>  # true | false
RUBRIC_REF  = <RUBRIC_REF>             # scoring_rubric applied
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_llm_judge]] | downstream | 0.66 |
| [[llm-judge-builder]] | related | 0.65 |
| p07_llm_judge | related | 0.54 |
| n00_judge_config_manifest | sibling | 0.54 |
| n00_llm_judge_manifest | sibling | 0.54 |
