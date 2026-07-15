---
id: p01_fse_kc_creation
kind: few_shot_example
8f: F3_inject
pillar: P01
title: "Few-Shot Example — Knowledge Card Creation"
version: 1.0.0
created: 2026-04-07
author: n04_knowledge
domain: knowledge-management
quality: null
tags: [few-shot, knowledge-card, template, creation-pattern]
tldr: "Input/output example showing how to create a high-density KC from a raw topic — demonstrates frontmatter, section order, density rules."
density_score: 0.94
updated: "2026-04-17"
related:
  - p01_kc_chain_of_thought
  - p01_kc_prompt_engineering_best_practices
  - p06_schema_kc_structure
  - p10_lr_chain_builder
  - p01_kc_chain
slots:
  new_input: "<the case the consuming LLM generalizes to>"
  expected_shape: "<the output contract>"
---

# Few-Shot Example — KC Creation

## Input

```
Topic: Chain-of-Thought Prompting
Domain: llm_patterns
Request: Create a knowledge card about chain-of-thought prompting
```

## Expected Output

```markdown
---
id: p01_kc_chain_of_thought
kind: knowledge_card
type: domain
pillar: P01
title: "Chain-of-Thought Prompting"
version: 1.0.0
created: 2026-04-07
author: n04_knowledge
domain: llm_patterns
quality: null
tags: [chain-of-thought, cot, reasoning, prompting]
tldr: "Elicit step-by-step reasoning by prefixing 'Let's think step by step' or providing worked examples — improves accuracy on math, logic, multi-hop QA."
keywords: [chain-of-thought, cot, step-by-step]
density_score: 0.93
---

# Chain-of-Thought Prompting

Technique that decomposes complex reasoning into intermediate steps.
Introduced by Wei et al. (2022). Two variants: zero-shot ("think step by step")
and few-shot (worked examples in prompt).

| Variant | Trigger | Best For | Accuracy Gain |
|---------|---------|----------|---------------|
| Zero-shot CoT | "Let's think step by step" suffix | Quick reasoning boost | +10-15% on GSM8K |
| Few-shot CoT | 2-3 worked examples | Complex multi-step | +20-30% on GSM8K |
| Auto-CoT | LLM generates own examples | No manual examples available | +15-20% on GSM8K |

## CEX Integration

Used in 8F pipeline at F1 (Focus): complex intents trigger CoT decomposition
before routing to builder. `cex_8f_motor.py` applies CoT for multi-kind intents.

See: `kc_prompting_patterns`, `kc_few_shot_learning`
```

## Why This Is Good

| Criterion | Score | Reason |
|-----------|-------|--------|
| Density | 0.93 | No filler. Every sentence adds value. |
| Frontmatter | Complete | All 14 required fields present. |
| Section order | Correct | H1 → Core (2 sentences) → Table → CEX Integration |
| Size | ~1.1KB | Well under 2KB focused limit |
| Cross-refs | Present | Links to 2 related KCs |
| Tables | Used | Comparison data in table, not prose |

## Anti-Pattern (What NOT to Do)

```markdown
# Chain-of-Thought Prompting

In this knowledge card, we will discuss chain-of-thought prompting,
which is an important technique in the field of AI. Chain-of-thought
prompting is a method that helps language models think more carefully
about problems by breaking them down into steps.

It is important to note that this technique was introduced in a
groundbreaking paper by researchers at Google Brain...
```

**Why this fails**: Meta-commentary ("In this KC we will discuss"), hedging ("It is important to note"), adjective stuffing ("groundbreaking"), no tables, no frontmatter, no cross-refs. Density: ~0.4.


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
| p01_kc_chain_of_thought | related | 0.51 |
| p01_kc_prompt_engineering_best_practices | related | 0.46 |
| p06_schema_kc_structure | downstream | 0.40 |
| p10_lr_chain_builder | downstream | 0.39 |
| p01_kc_chain | downstream | 0.36 |
