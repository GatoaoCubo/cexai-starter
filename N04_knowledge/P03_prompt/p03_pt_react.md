---
id: prompt_technique_react
kind: prompt_technique
pillar: P03
title: "ReAct -- Reasoning and Acting"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
domain: prompt_engineering
quality: null
technique_type: reasoning-acting
difficulty_level: intermediate
example_use_case: "Tool-using agent answers a multi-hop question by searching, observing results, and reasoning iteratively until resolved."
tags: [react, reasoning, acting, tool-use, agent, prompt-technique, P03]
tldr: "Interleave Thought/Action/Observation loops so the model reasons before each tool call and updates its plan from each result."
source: "github.com/dair-ai/Prompt-Engineering-Guide"
source_author: "DAIR.AI"
source_license: "MIT"
related:
  - p01_kc_repo_assimilation_candidates
  - 8f-reasoning
keywords: [react, reasoning, acting, thought-action-observation, tool-use, agent, multi-hop]
density_score: 0.88
---

## Overview

ReAct (Yao et al., ICLR 2023) interleaves **reasoning traces** and **actions**
in a single output stream. Three labeled steps alternate in a loop:

- **Thought** -- the model articulates reasoning or plan before acting.
- **Action** -- the model calls an external tool (search, calculator, API).
- **Observation** -- the tool result is injected back; the model reads and loops.

The loop runs until the model emits `Action: Finish[answer]`. Reasoning grounds
actions; observations update reasoning -- reducing hallucination on multi-hop tasks.

## Application Context

**Use when:** task requires external tools; multi-hop retrieval is needed;
agent transparency (auditable Thought traces) is required; maps to 8F F5 CALL.

**Do NOT use when:** no tools available; pure generation suffices; latency is
critical; context window budget is too tight for multi-turn Thought/Obs cycles.

## Prompt Scaffold

```
Answer using Thought / Action / Observation steps.

Available actions: Search[query], Lookup[term], Calculate[expr], Finish[answer]

Thought: <reasoning>
Action: <one action>
Observation: <tool result>
... (repeat)
Thought: I now know the final answer.
Action: Finish[<answer>]
```

After parsing each `Action`, run the tool, append `Observation: <result>`,
re-invoke the model. Loop until `Action: Finish` is detected.

## Example

```
Question: Who directed the film where Anthony Hopkins plays a forensic
psychiatrist hunting a serial killer?

Thought: Sounds like Silence of the Lambs. Confirm the director.
Action: Search[Silence of the Lambs film director]
Observation: Directed by Jonathan Demme (1991).
Thought: Confirmed. Hopkins plays Hannibal Lecter.
Action: Finish[Jonathan Demme]
```

## CEXAI Mapping

| CEXAI Concept | ReAct Mapping |
|-------------|---------------|
| F5 CALL | Action step -- model selects and invokes a tool |
| F3 INJECT | Observation -- tool output re-injected into context |
| F4 REASON | Thought step -- model plans before acting |
| `agent` kind | Agent running ReAct as its execution core |
| `workflow` kind | Multi-step ReAct traces compiled into a pipeline |

ReAct IS the agent F5 CALL loop: Thought (F4 REASON) -> Action (F5 CALL) ->
Observation (F3 INJECT) -> loop. The Thought/Action/Observation triple maps
1:1 to the 8F F4/F5/F3 sub-cycle inside any tool-using agent.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_repo_assimilation_candidates]] | upstream | 0.55 |
| [[8f-reasoning]] | upstream | 0.70 |
