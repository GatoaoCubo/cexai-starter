---
id: p03_ch_builder_pipeline
kind: chain
8f: F6_produce
pillar: P03
title: Prompt Chain -- Builder Pipeline
version: 1.0.0
created: 2026-03-30
updated: 2026-03-30
author: builder_agent
domain: meta-construction
quality: null
tags: [chain, builder, N03]
tldr: "4-step LLM chain for 8F pipeline: CLASSIFY (F4, temp=0.3, 500tok), BUILD (F6, temp=0.7, 4000tok), VALIDATE (F7, temp=0.0, cheap model, 500tok), RETRY (conditional, temp=0.5). Steps 1-3 and 5 are deterministic; only these 4 are LLM calls."
keywords: [prompt chain, llm calls, deterministic, yaml frontmatter, structured body, token budget, artifact generation, validation gates, motor resolved]
density_score: 0.88
related:
  - p12_wf_builder_8f_pipeline
  - p10_lr_chain_builder
  - bld_architecture_chain
---

# Prompt Chain: Builder Pipeline

## Overview

4 LLM calls in the 8F pipeline. Steps 1-3 and 5 are deterministic.

## Step 1: CLASSIFY (F4 REASON)

    Given kind={{kind}}, constraints={{constraints}}, knowledge={{kc_summary}}:
    Plan sections, references, structure.
    Output 100-200 word construction plan.

Temperature: 0.3 | Max tokens: 500

## Step 2: BUILD (F6 PRODUCE)

    Using plan={{plan}}, tools={{tools}}, knowledge={{full_kc}}:
    Produce complete artifact with YAML frontmatter and structured body.
    Follow builder output template for {{kind}}.

Temperature: 0.7 | Max tokens: 4000

## Step 3: VALIDATE (F7 GOVERN)

    Check artifact against gates H01-H07:
    {{artifact_text}}
    Report: pass/fail per gate, overall score, issues list.

Temperature: 0.0 | Max tokens: 500 | Model: cheapest-tier available

## Step 4: RETRY (if needed)

    Artifact failed these gates: {{issues}}
    Revise to fix specific issues. Keep what passed.

Temperature: 0.5 | Max tokens: 4000

## Token Budget Per Step

| Step | Input Tokens | Output Tokens | Model | Cost Driver |
|------|-------------|---------------|-------|-------------|
| CLASSIFY | ~2000 (constraints+KC summary) | 500 | mid-tier | Low -- planning only |
| BUILD | ~4000 (plan+full KC+tools) | 4000 | mid-tier | High -- artifact generation |
| VALIDATE | ~5000 (full artifact text) | 500 | cheap-tier | Low -- structural check |
| RETRY | ~6000 (artifact+issues) | 4000 | Same as BUILD | Conditional -- only on soft fail |

Total per artifact (no retry): ~12K tokens. With 1 retry: ~22K tokens.

## Step Context Passing

Each step receives the previous step's output as context:
- CLASSIFY output (plan) is injected as `{{construction_plan}}` into BUILD
- BUILD output (artifact text) is injected as `{{artifact_text}}` into VALIDATE
- VALIDATE output (issues list) is injected as `{{issues}}` into RETRY
- No step has access to raw user input -- only the resolved kind and constraints

## Worked Example

### Building one knowledge_card end-to-end (no retry path)

```
INPUT (from F1 + F3):
  kind        = knowledge_card
  constraints = max_bytes=8192, density>=0.85
  kc_summary  = "embedding strategies for retrieval"
  full_kc     = <KC body, ~3KB>
  tools       = [retriever, compile, doctor]

Step 1 CLASSIFY (mid-tier, temp=0.3, 500 max-tokens)
  Output: "Plan: 4 sections (Definition, Strategies, Tradeoffs,
           When-to-Use), 2 tables, density target 0.88, ~6KB total"

Step 2 BUILD (mid-tier, temp=0.7, 4000 max-tokens)
  Output: <full markdown artifact, ~5800 bytes, density 0.89>

Step 3 VALIDATE (cheap-tier, temp=0.0, 500 max-tokens)
  Output: {pass: true, score: 9.0, gates_passed: 6/6, gates_failed: 0}

Step 4 RETRY: SKIPPED (validate passed)

TOTAL TOKENS: 11,800  (no retry path)
```

### Retry path (validate fails)

```
Step 3 VALIDATE returns:
  {pass: false, score: 7.6, gates_failed: ["H05_density_below_floor"]}

Step 4 RETRY (mid-tier, temp=0.5, 4000 max-tokens)
  Input: original artifact + issue: "density 0.78 < 0.85 floor"
  Output: <revised artifact, density 0.87>

Step 3 VALIDATE (re-run): {pass: true, score: 8.7}

TOTAL TOKENS: 21,800  (one retry)
```

## Edge Cases

| Edge case | Behavior |
|-----------|----------|
| BUILD step exceeds 4000 token budget mid-stream | Truncate at 4000; VALIDATE will catch incomplete frontmatter (H01) and trigger RETRY |
| VALIDATE returns score=8.05 (just above floor) | PASS -- no retry; floor is 8.0 inclusive |
| Same gate fails twice in a row (RETRY then re-VALIDATE fails again) | Hand off to a revision_loop_policy -- 3-cycle limit; if exhausted, escalate |
| `kind` resolved to a kind without builder ISOs | Identity load fails before chain runs; chain is never invoked |
| Network failure between Step 2 and Step 3 | Step 3 is idempotent -- safe to retry the validate call without re-building |
| RETRY budget hit but score now equals 7.99 | Below floor; BLOCK; artifact NOT saved; nucleus signals `status="failed"`, `score=7.99` |

## Invariants

1. **Steps 1-3 always run; Step 4 is conditional**. Skipping Step 3 (VALIDATE) is forbidden -- it is the quality gate.
2. **Each step has a strict token budget**; no step is allowed to exceed its declared `max_tokens`.
3. **Step 3 (VALIDATE) MUST use a different/cheaper model than Step 2** (BUILD) -- structural validation does not need full reasoning capacity.
4. **No step receives raw user input** -- upstream steps have already resolved everything.
5. **Step output is the next step's input** -- no shared mutable state; each call is referentially transparent.
6. **Total token budget is bounded by `max_retries`**: at most `~12K + max_retries * 10K` per artifact (with current settings: max 32K with 2 retries).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_wf_builder_8f_pipeline]] | downstream | 0.36 |
| [[p10_lr_chain_builder]] | downstream | 0.29 |
| [[bld_architecture_chain]] | downstream | 0.28 |
