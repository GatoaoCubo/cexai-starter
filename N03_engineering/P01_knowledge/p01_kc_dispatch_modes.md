---
id: p01_kc_dispatch_modes
kind: knowledge_card
8f: F3_inject
primary_8f: INJECT
title: CEX Dispatch Modes Comparison
version: 1.1.0
quality: null
pillar: P01
tags: [dispatch, dispatch-modes, grid, crew, sweep, cascade, concurrency, aider, claude, knowledge_card]
tldr: "Reference card comparing CEX dispatch modes (Claude Grid + Aider grid/crew/sweep/cascade) on concurrency/model/cost/throughput -- so you pick the right execution topology per workload."
when_to_use: "Load when choosing how to dispatch a task (parallel vs sequential, Claude vs Aider). Consult for 'which dispatch mode fits this workload's concurrency and cost profile?'"
keywords: [claude opus, aider grid, aider crew, aider sweep, aider cascade, parallel execution, sequential execution, context window, resource throttling, batch processing]
density_score: 1.0
related:
  - kc_workflow_run_crate
  - kc_8f_pipeline_implementation
  - p01_kc_atom_28_code_agents
  - p01_kc_batching
  - n06_hybrid_review2_final
---

# CEX Dispatch Modes Comparison

The CEX system supports multiple dispatch modes for task execution. Each mode has distinct characteristics that make them suitable for different workloads. Below is a comparison of key dispatch modes:

| Mode           | Concurrency | Model              | Cost       | Throughput | Best Use Case                          |
|----------------|-------------|--------------------|------------|------------|----------------------------------------|
| **Claude Grid** | Parallel    | Claude Opus        | High       | High       | Complex tasks requiring parallelism    |
| **Aider Grid**  | Parallel    | Aider              | Medium     | Medium     | Batch processing with moderate complexity |
| **Aider Crew**  | Parallel    | Aider              | Medium     | High       | Parallelizable tasks with shared context |
| **Aider Sweep** | Sequential  | Aider              | Low        | Medium     | Linear workflows with dependent steps  |
| **Aider Cascade** | Sequential | Aider              | Low        | Low        | Dependent tasks requiring strict order |

## Mode Details (beyond the table)

The comparison table above captures concurrency, model, cost, and throughput per
mode. The distinguishing axis not in the table is **context coupling**:

- **Claude Grid** isolates each cell in its own 1M-context nucleus -- best when
  cells must NOT see each other (research, large independent fan-out).
- **Aider Crew** is the only parallel mode that *shares* context across cells --
  pick it when cells need a common ground truth (docs generation, linked edits).
- **Aider Sweep** retains memory across a loose sequence; **Aider Cascade** adds
  strict dependency tracking so step N cannot start until N-1 is verified.

Default to the cheapest mode whose coupling + ordering guarantees match the work.

### How to choose a mode

```text
Decision order (pick the FIRST that matches):
1. Tasks are independent AND complex      -> Claude Grid (full parallel, 1M ctx).
2. Tasks are independent AND batch-simple -> Aider Grid (throttled parallel).
3. Tasks are parallel BUT share context   -> Aider Crew (context-preserving).
4. Tasks are dependent, loose ordering     -> Aider Sweep (sequential + memory).
5. Tasks are dependent, STRICT ordering    -> Aider Cascade (strict sequence).
Cost rises with concurrency + model tier; default to the cheapest mode that
still satisfies the dependency + complexity constraints above.
```

This card is read at F3 INJECT to ground a dispatch decision; it does not itself
dispatch (see the orchestrator rules + `kc_8f_pipeline_implementation`).

## Boundary

Conhecimento destilado, estatico, versionado. NAO eh instrucao, template, ou configuracao.

## 8F Pipeline Function

Primary function: **INJECT** -- this reference is injected into reasoning to pick a topology.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| kc_workflow_run_crate | sibling | 0.30 |
| [[kc_8f_pipeline_implementation]] | sibling | 0.27 |
| p01_kc_atom_28_code_agents | sibling | 0.25 |
| p01_kc_batching | sibling | 0.23 |
| n06_hybrid_review2_final | downstream | 0.20 |
