---
quality: null
id: p01_kc_dspy
kind: knowledge_card
8f: F3_inject
kc_type: industry_reference
pillar: P01
nucleus: n04
version: 1.0.0
created: "2026-05-05"
updated: "2026-05-05"
author: n04_knowledge
title: "DSPy -- Programmatic Prompts and Compiled Pipelines"
domain: ai_agent_systems
subdomain: industry_reference
tags: [dspy, programmatic_prompts, signature, module, optimizer, compiler, miprov2, bootstrap, industry_reference, comparison]
tldr: "DSPy reframes prompt engineering as software engineering: declare typed signatures (input -> output), compose modules (predict, chain-of-thought, react), then let an optimizer compile prompts and few-shots from a small training set. CEXAI adopts the signature/module/optimizer trinity and elevates the compilation idea into the prompt_compiler kind that runs at F1 CONSTRAIN."
keywords: [dspy, signature, module, predict, chainofthought, react, optimizer, miprov2, bootstrapfewshot, copro, compile, teleprompter, metric, programmatic prompt, declarative]
density_score: 0.89
related:
  - p01_kc_langchain
  - p01_kc_crewai
  - prompt-compiler-builder
---

# DSPy — Programmatic Prompts and Compiled Pipelines

## Definition

DSPy (Declarative Self-improving Python) is an open-source framework from Stanford NLP (Omar Khattab et al., 2023) that treats prompt engineering as a *programming* problem rather than a string-tweaking problem. Instead of writing English instructions, you declare typed `Signature`s ("question -> answer with rationale"), compose them into `Module`s, and run an `Optimizer` (a "teleprompter") that compiles the actual prompts, demonstrations, and routing decisions from a small training set + a metric. The result is a self-improving pipeline whose prompts are generated, not hand-written.

## Key Concepts

| Primitive | Meaning | CEXAI analogue |
|-----------|---------|----------------|
| `Signature` | Typed declaration: input fields → output fields, with field descriptions | `input_schema` + `response_format` (P06) |
| `Module` | Composable unit: `Predict`, `ChainOfThought`, `ReAct`, `ProgramOfThought`, `MultiChainComparison` | `prompt_template` + `chain` (P03/P12) |
| `Predict` | Single LLM call against a signature | one-shot `prompt_template` |
| `ChainOfThought` | Adds rationale field before output | `reasoning_strategy: cot` |
| `ReAct` | Reason-act-observe loop with tools | `agent` (P02) + `workflow` (P12) |
| `Example` | A `(input, output)` pair used as training data | `few_shot_example` (P03) + `eval_dataset` (P07) |
| `Metric` | Scores a prediction against the gold answer | `eval_metric` (P07) + `scoring_rubric` |
| `Teleprompter` / `Optimizer` | Compiles prompts: `BootstrapFewShot`, `MIPROv2`, `COPRO`, `BootstrapFinetune` | `prompt_optimizer` kind (P03) |
| `compile()` | Runs the optimizer; returns a prompt-compiled program | F1 CONSTRAIN + `cex_compile.py` |
| `dspy.Settings` | Global LM, cache, retrievers configuration | `model_provider` + `inference_config` |
| `Assertions` / `Suggestions` | Soft and hard constraints on output (retry on violation) | `guardrail` + `output_validator` (P11/P05) |

## What CEXAI Adopts

1. **Signature-first design.** Every artifact in CEXAI has a typed input/output schema declared in frontmatter or in the corresponding `input_schema` / `response_format` kind. This is the DSPy idea applied at the artifact level.
2. **Compilation is the central metaphor.** CEXAI's `prompt_compiler` kind (canonical instance: `p03_pc_cex_universal.md`) lifts the user's natural-language intent into a typed `{kind, pillar, nucleus, verb}` tuple before any LLM call — that is DSPy's `compile()` shifted to F1 CONSTRAIN.
3. **Modules over megaprompts.** CEXAI breaks reasoning into small composable kinds (`prompt_template`, `chain`, `reasoning_strategy`, `reasoning_trace`) rather than one wall-of-text system prompt. This mirrors DSPy's module decomposition.
4. **Metric-driven optimization.** CEXAI's F7 GOVERN runs `eval_metric` against `eval_dataset` to score artifacts; the `prompt_optimizer` kind exists explicitly to do DSPy-style search over prompt variants when a 9.0+ floor must be met.
5. **Few-shot bootstrap pattern.** When a builder has matching examples, F3 INJECT seeds them — equivalent to `BootstrapFewShot` automatically populating demonstrations from the training set.
6. **Assertions as runtime contracts.** DSPy's `dspy.Assert` is conceptually identical to CEXAI's `guardrail` kind (P11) — soft constraint with retry on violation.

## What CEXAI Differs

1. **Compiled artifacts are versioned files, not in-memory programs.** A DSPy compiled program lives in a Python pickle / JSON cache. CEXAI's compiled prompts are `.md` artifacts with frontmatter, semver, and git history — peer-scored, auditable, transferable.
2. **Compilation runs at intent-resolution time, not training time.** DSPy compiles offline against a training set then ships. CEXAI's `cex_intent_resolver.py` + `prompt_compiler` resolve every user phrase at F1 in zero tokens (Python-first), and only escalate to LLM when confidence < 60%. The "training set" is the kinds_meta registry itself.
3. **Multi-modal optimizer family.** DSPy ships ~6 teleprompters (BootstrapFewShot, MIPROv2, COPRO, BootstrapFinetune, etc.). CEXAI's `prompt_optimizer` kind is open-ended; we add `evolve` (heuristic + agent), `revision_loop_policy` (gate-driven retries), and council voting (cross-provider) — broader than DSPy's exclusively training-set-driven optimizers.
4. **Optimization gates on quality, not just metric.** DSPy optimizes a numeric metric. CEXAI optimizes against H01-H06 universal hooks + kind-specific evals + 5D (D1-D5 dimensions) + COUNCIL divergence — multi-dimensional acceptance.
5. **Modules are domain-typed, not generic.** DSPy modules are domain-agnostic (Predict, CoT, ReAct work anywhere). CEXAI modules are *kinds* in a 12-pillar taxonomy — a `chain` is always P12 orchestration, never confused with a `prompt_template` (P03). This narrows reuse but eliminates ambiguity.
6. **Runtime portability.** A DSPy program runs in Python with `dspy.settings.configure(lm=...)`. A CEXAI compiled artifact runs under any of Claude/Codex/Gemini/Ollama via the prompt-compiler tuple — no Python at the edge.
7. **Knowledge is permanent.** DSPy compiles once and discards intermediate state. CEXAI persists every F3 injection, every F7 score, every F7b learning record — the system improves across sessions, not just within one compile.

## When to Reach for DSPy Directly

Use DSPy when you have: (a) a labelled dataset of >50 examples, (b) a clear scalar metric, and (c) a willingness to run an optimization loop in Python before deploying. The MIPROv2 + BootstrapFewShot combo is genuinely state-of-the-art for narrow tasks. For everything else — open-ended creative work, system-level orchestration, multi-runtime deployment — write CEXAI artifacts. The compilation idea applies, but the substrate must outlive the Python process.

## Related Artifacts

| Artifact | Relationship |
|----------|-------------|
| [[p01_kc_langchain]] | sibling industry reference |
| [[p01_kc_crewai]] | sibling industry reference |
| p01_kc_prompt_compiler | direct CEXAI descendant |
| prompt-compiler-builder | builder for the same idea |
