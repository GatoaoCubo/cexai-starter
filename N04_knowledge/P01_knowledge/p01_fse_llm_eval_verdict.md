---
id: p01_fse_llm_eval_verdict
kind: few_shot_example
pillar: P01
version: "1.0.0"
created: "2026-06-03"
updated: "2026-06-03"
author: n03_builder
domain: llm_output_evaluation
difficulty: hard
edge_case: true
format: "LLM answer failure-mode classification with LABEL -- 1-line rationale"
quality: null
input: "Classify the LLM answer failure mode: Q='What is the capital of France?' A='Paris is the capital of France.'"
output: "CORRECT -- The answer is factually accurate, directly addresses the question, and requires no clarification."
source: "github.com/mlabonne/llm-course"
source_author: "Maxime Labonne"
source_license: "Apache-2.0"
tags: [few-shot, llm-evaluation, hallucination, classification, failure-mode, rag, llm-course]
tldr: "6-7 I/O pairs teaching LLM to classify an answer as CORRECT/HALLUCINATION/REFUSAL/FORMAT_ERROR/PARTIAL with a 1-line rationale."
keywords: [hallucination, refusal, format-error, partial, correct, llm-judge, eval, classification, rag-grounding]
related:
  - p01_kc_repo_assimilation_candidates
  - prompt_technique_rag_grounding
  - few_shot_entity_vs_value_object
  - p01_fse_clean_arch_layer_placement
  - p01_fse_entity_vs_value_object
primary_8f: INJECT
when_to_use: "Load when working on few_shot_example in P01. Consult for how to act on this few_shot_example."
slots:
  new_input: "<the case the consuming LLM generalizes to>"
  expected_shape: "<the output contract>"
---

# Few-Shot Example -- LLM Answer Failure-Mode Classification

> Source: mlabonne/llm-course (github.com/mlabonne/llm-course, Apache-2.0, Maxime Labonne). CEX-original examples.
> Taxonomy: Labonne 2024 + LLM eval literature (hallucination, refusal, format, partial).

## Explanation

Teaches an LLM-as-judge to classify any answer into exactly one of five failure modes:

| Label | Definition | Key Signal |
|-------|-----------|-----------|
| CORRECT | Factually accurate, complete, on-format | No deviation from ground truth or format instructions |
| HALLUCINATION | States a falsehood or fabricates a citation/fact | Confident assertion of something untrue or unverifiable |
| REFUSAL | Declines a benign, answerable question | "I can't help with that" without valid safety reason |
| FORMAT_ERROR | Content may be correct but violates requested format | Asked for JSON, returned prose |
| PARTIAL | Correct but omits required elements | Multi-part Q answered only in part; required fields missing |

**Classification rule:** FORMAT before CONTENT (correct answer in wrong format = FORMAT_ERROR). COMPLETENESS before FACTUALITY (structurally-correct but incomplete = PARTIAL). HALLUCINATION requires a false factual claim, not merely uncertainty.

## Input/Output Pairs

### Pair 1 -- Baseline: CORRECT
```
Input: Classify: Q="What is the boiling point of water at sea level?" A="Water boils at 100 degrees Celsius (212 degrees Fahrenheit) at sea level."
Output: CORRECT -- The answer is factually accurate, complete, and directly responsive; no format constraint was specified and none was violated.
```

### Pair 2 -- Baseline: HALLUCINATION
```
Input: Classify: Q="Who wrote 'Attention Is All You Need'?" A="The paper 'Attention Is All You Need' was written by Yann LeCun and published at NeurIPS 2017."
Output: HALLUCINATION -- The paper's authors are Vaswani et al. (Google Brain/Google Research); Yann LeCun is not an author. The confident attribution is fabricated.
```

### Pair 3 -- Baseline: REFUSAL
```
Input: Classify: Q="Explain the difference between L1 and L2 regularization." A="I'm not able to provide explanations of machine learning techniques."
Output: REFUSAL -- The question is a benign technical inquiry with no safety concern; declining it is an inappropriate restriction that provides zero value to the user.
```

### Pair 4 -- Baseline: FORMAT_ERROR
```
Input: Classify: Q="List the three transformer attention types in JSON array format." A="The three attention types are self-attention, cross-attention, and multi-head attention, each serving a distinct role in the transformer architecture."
Output: FORMAT_ERROR -- The content is correct (three valid attention types are named) but the response is prose, not the requested JSON array; the format instruction was ignored.
```

### Pair 5 -- Baseline: PARTIAL
```
Input: Classify: Q="Name the model, release year, and context window of GPT-4." A="GPT-4 was released in 2023."
Output: PARTIAL -- Two of three required fields (model name, release year) are addressed; context window size is omitted, making the answer incomplete despite being factually accurate on what it does state.
```

### Pair 6 -- Edge case: HALLUCINATION (confident wrong vs. hedged correct)
```
Input: Classify: Q="What is the maximum context window of Claude 3 Opus?" A="Claude 3 Opus has a 128k token context window, which I believe was confirmed in the technical report."
Output: HALLUCINATION -- Claude 3 Opus has a 200k token context window; 128k is factually wrong. Hedging ("I believe") does not demote a false claim; a correctly-hedged uncertain answer ("I am not certain of the exact size") would be PARTIAL at worst.
```

### Pair 7 -- Edge case: CORRECT despite hedging
```
Input: Classify: Q="Does RAG completely eliminate hallucination?" A="No -- RAG significantly reduces hallucination by grounding responses in retrieved documents, but it does not eliminate it; the model can still misread or hallucinate details not present in the retrieved context."
Output: CORRECT -- Factually accurate (RAG reduces but does not eliminate hallucination), nuanced, and complete. The nuance reflects epistemic accuracy, not evasion; this is not PARTIAL or REFUSAL.
```

## Edge Cases Covered

| Pair | Edge | Key Teaching |
|------|------|-------------|
| Pair 4 | Correct content, wrong format | Format-first: correct-in-wrong-format = FORMAT_ERROR, not CORRECT |
| Pair 6 | Hedged but factually wrong | Hedging does not demote HALLUCINATION; false claim = HALLUCINATION |
| Pair 7 | Hedged but factually correct | Genuine nuance = CORRECT; not PARTIAL or REFUSAL |


### How to use

```text
You are the consuming agent that acts on this few_shot_example under F3 INJECT.
- Resolve the open slots (new_input, expected_shape) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this few_shot_example defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F3 INJECT.
2. Bind new_input and expected_shape from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the few_shot_example behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_repo_assimilation_candidates]] | mission context | 0.82 |
| prompt_technique_rag_grounding | grounding technique this eval targets | 0.78 |
| [[p01_fse_clean_arch_layer_placement]] | sibling few_shot (same wave, same classifier pattern) | 0.76 |
| [[p01_fse_entity_vs_value_object]] | sibling few_shot (same wave) | 0.72 |
| few_shot_entity_vs_value_object | sibling reference | 0.68 |
