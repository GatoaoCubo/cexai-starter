---
id: p01_kc_prompt_engineering_taxonomy
kind: knowledge_card
card_type: domain_kc
8f: F3_inject
primary_8f: INJECT
title: "Prompt Engineering Taxonomy -- Cited Reference for 6 Core Techniques"
version: 2.0.0
quality: null
pillar: P01
nucleus: n01
created: 2026-04-13
updated: 2026-05-02
domain: research-intelligence
tags: [prompt-engineering, zero-shot, few-shot, cot, tot, react, self-consistency, taxonomy, n01]
tldr: "6 canonical prompt techniques mapped to seminal papers (Brown 2020, Wei 2022, Yao 2023, Wang 2022) with measured accuracy uplift, token cost multiplier, and CEX usage in the 8F pipeline."
when_to_use: "When choosing reasoning strategy for a builder; when comparing token cost of CoT vs ToT; when designing a chain that needs verifiable accuracy; when teaching prompt engineering vocabulary"
axioms:
  - "ALWAYS cite the originating paper when introducing a technique -- the year and authors anchor credibility and reveal vintage"
  - "ALWAYS measure cost-uplift -- ToT is 5-10x token cost vs zero-shot for marginal gain on simple tasks"
  - "NEVER conflate ReAct (reason+act) with chain-of-thought (reason only) -- ReAct requires tool execution"
  - "NEVER use self-consistency for tasks where verifier cannot detect divergence -- waste of tokens"
keywords: [zero-shot, few-shot, chain-of-thought, tree-of-thought, react, self-consistency, prompt engineering, gpt-3, in-context learning, reasoning]
density_score: 0.95
related:
  - kc_reasoning_strategy
  - reasoning-strategy-builder
---

# Prompt Engineering Taxonomy

## Overview

This knowledge card maps six canonical prompt engineering techniques to their seminal papers, measured accuracy uplift on standard benchmarks, and recommended CEX 8F usage. It is the canonical reference cited from `reasoning_strategy_n01.md` and `system_prompt_n01.md`.

## Core Techniques (Cited)

### 1. Zero-shot

| Field | Value |
|-------|-------|
| Definition | Direct task instruction with no examples |
| Originating paper | Brown et al., "Language Models are Few-Shot Learners," NeurIPS 2020 (arxiv 2005.14165) |
| Accuracy benchmark | GPT-3 175B: 64.3% on TriviaQA zero-shot |
| Token cost multiplier | 1.0x (baseline) |
| Best for | Simple classification, format conversion, single-step Q&A |
| CEX 8F usage | F1 CONSTRAIN, F5 CALL when intent is unambiguous |

### 2. Few-shot (in-context learning)

| Field | Value |
|-------|-------|
| Definition | 1-3 (or k) input/output examples in the prompt |
| Originating paper | Brown et al., "Language Models are Few-Shot Learners," NeurIPS 2020 |
| Accuracy benchmark | GPT-3 175B: 71.2% on TriviaQA at k=64 (vs 64.3% zero-shot) |
| Token cost multiplier | 1.5-3x (depends on k and example length) |
| Best for | Complex format requirements, named-entity extraction, structured output |
| CEX 8F usage | F2 BECOME (load builder ISOs as few-shot), F6 PRODUCE for templated output |

### 3. Chain-of-Thought (CoT)

| Field | Value |
|-------|-------|
| Definition | Prompt explicitly asks for step-by-step reasoning before answer |
| Originating paper | Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models," NeurIPS 2022 (arxiv 2201.11903) |
| Accuracy benchmark | PaLM 540B: 56.5% -> 74.4% on GSM8K (math reasoning) with 8-shot CoT |
| Token cost multiplier | 3-5x output tokens (reasoning + answer) |
| Best for | Math, multi-step logic, deductive reasoning, planning |
| CEX 8F usage | F4 REASON when intent involves multi-step inference |

### 4. Tree-of-Thoughts (ToT)

| Field | Value |
|-------|-------|
| Definition | Explore multiple reasoning branches with state evaluation and backtracking |
| Originating paper | Yao et al., "Tree of Thoughts: Deliberate Problem Solving with Large Language Models," NeurIPS 2023 (arxiv 2305.10601) |
| Accuracy benchmark | GPT-4: 4% (CoT) -> 74% (ToT) on Game of 24; 16x improvement |
| Token cost multiplier | 5-15x (branch generation + state evaluation) |
| Best for | Open-ended search, planning under uncertainty, creative ideation |
| CEX 8F usage | RARE -- reserve for stuck-state F4 REASON when CoT plateaus |

### 5. ReAct (Reasoning + Acting)

| Field | Value |
|-------|-------|
| Definition | Interleave reasoning traces with tool actions in observation/thought/action loops |
| Originating paper | Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," ICLR 2023 (arxiv 2210.03629) |
| Accuracy benchmark | GPT-3: 27.4% -> 35.1% on HotpotQA (multi-hop QA with tools) |
| Token cost multiplier | 2-4x (reasoning + tool call overhead) |
| Best for | Tool-augmented agents, retrieval-required tasks, agent loops |
| CEX 8F usage | F5 CALL when builder must invoke external tools mid-reasoning |

### 6. Self-Consistency

| Field | Value |
|-------|-------|
| Definition | Sample N reasoning paths, majority-vote the final answer |
| Originating paper | Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models," ICLR 2023 (arxiv 2203.11171) |
| Accuracy benchmark | PaLM 540B: 74.4% (CoT) -> 86.6% on GSM8K with 40 samples |
| Token cost multiplier | N x CoT cost (typically 5-40x) |
| Best for | High-stakes math/logic, single verifiable answer, no human review |
| CEX 8F usage | F7 GOVERN escalation when single-path quality < 8.0; capped N=3 by default |

## Comparison Table (consolidated)

| Technique | Year | Accuracy uplift (relative) | Token cost (relative) | Cost-effectiveness |
|-----------|------|----------------------------|----------------------|-------------------|
| Zero-shot | 2020 | baseline | 1.0x | High for simple tasks |
| Few-shot | 2020 | +7-15% on TriviaQA | 1.5-3x | High for templated tasks |
| CoT | 2022 | +18% on GSM8K | 3-5x | Highest for math/logic |
| Self-consistency (N=40) | 2022 | +12% over CoT on GSM8K | 5-40x | High when verifier scarce |
| ReAct | 2023 | +8% on HotpotQA | 2-4x | High for tool-augmented |
| ToT | 2023 | +70% on Game of 24 | 5-15x | Lowest -- reserve for stuck state |

## CEX Usage Map

| 8F Function | Default Technique | Escalation Path |
|-------------|-------------------|-----------------|
| F1 CONSTRAIN | zero-shot | n/a (deterministic intent resolution) |
| F2 BECOME | few-shot (12 ISOs) | n/a |
| F3 INJECT | few-shot (KC examples) | n/a |
| F4 REASON | CoT | self-consistency if quality < 8.5 |
| F5 CALL | ReAct | n/a |
| F6 PRODUCE | few-shot template | n/a |
| F7 GOVERN | zero-shot rubric scoring | self-consistency for divergence > 0.3 |
| F7c COUNCIL | self-consistency (3 judges) | ToT for stuck consensus |
| F8 COLLABORATE | zero-shot signal | n/a |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|--------------|------------------|
| ToT for simple Q&A | 15x cost, no accuracy gain | Use zero-shot |
| Self-consistency without verifier | Cannot pick correct answer from N samples | Use single CoT + human review |
| Few-shot with > 32 examples | Token budget exhausted; recall plateaus | Use RAG retrieval instead |
| ReAct without tool registry | Halucinated tool names; runtime error | Pin tool registry before ReAct |

## Sources (Primary Papers)

- Brown et al. (2020), "Language Models are Few-Shot Learners," NeurIPS. arxiv 2005.14165
- Wei et al. (2022), "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models," NeurIPS. arxiv 2201.11903
- Wang et al. (2022), "Self-Consistency Improves Chain of Thought Reasoning in Language Models," ICLR 2023. arxiv 2203.11171
- Yao et al. (2023a), "ReAct: Synergizing Reasoning and Acting in Language Models," ICLR. arxiv 2210.03629
- Yao et al. (2023b), "Tree of Thoughts: Deliberate Problem Solving with Large Language Models," NeurIPS. arxiv 2305.10601

## Sources (Surveys)

- Schulhoff et al. (2024), "The Prompt Report: A Systematic Survey of Prompting Techniques," arxiv 2406.06608 (358 techniques cataloged)
- Sahoo et al. (2024), "A Systematic Survey of Prompt Engineering in Large Language Models," arxiv 2402.07927

## Boundary

Knowledge card -- distilled, static, versioned. NOT an instruction, template, or configuration. Implementation guidance lives in `reasoning_strategy_n01.md`.

## 8F Pipeline Function

Primary function: **INJECT** -- loaded at F3 INJECT when builder must select reasoning technique.

### How to use

```text
ROLE: You are an LLM selecting a prompting technique from this taxonomy.
ACT:
  - Map the task to a technique class (reasoning / ICL / refinement / decomposition).
  - Prefer the simplest technique that meets the accuracy need; escalate only if needed.
  - Combine techniques only when each adds a distinct, justified gain.
OUTPUT: a chosen prompting technique tied to the task requirement.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_reasoning_strategy]] | sibling | 0.45 |
| p01_kc_chain_of_thought | sibling | 0.40 |
| [[reasoning-strategy-builder]] | downstream | 0.38 |
| p01_kc_prompt_engineering_best_practices | sibling | 0.35 |
| kc_prompt_technique | sibling | 0.32 |
