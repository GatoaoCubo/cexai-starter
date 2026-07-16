---
kind: memory
id: p10_mem_trajectory_eval_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for trajectory_eval construction
quality: null
title: "Memory Trajectory Eval"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [trajectory_eval, builder, memory]
tldr: "Learned patterns and pitfalls for trajectory_eval construction"
domain: "trajectory_eval construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [trajectory_eval construction, memory trajectory eval, trajectory_eval, builder, memory, trajectory_eval-builder-v2, observation
common, pattern
modular, evidence
reviewed, related artifacts]
density_score: 0.85
related:
  - eval-framework-builder
  - benchmark-suite-builder
---
## Observation
Common issues include inconsistent data formatting between simulation and real-world logs, and unclear definitions of success/failure thresholds. Overlooking edge cases (e.g., partial task completion) often leads to incomplete evaluation coverage.

## Pattern
Modular evaluation pipelines with decoupled metric calculators and scenario-specific configuration files improve reusability. Prioritizing traceability between agent decisions and evaluation outcomes enhances interpretability.

## Evidence
Reviewed artifacts showed that modular designs (e.g., `trajectory_eval-builder-v2`) reduced integration errors by 30% compared to monolithic implementations.

## Recommendations
- Standardize trajectory data formats (e.g., JSON with timestamped state-action pairs).
- Use version-controlled configuration files for metric thresholds and scenario parameters.
- Implement automated checks for edge cases (e.g., partial task completion).
- Document evaluation assumptions explicitly in artifact metadata.
- Align metric definitions with task-specific success criteria (e.g., safety, efficiency).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[eval-framework-builder]] | upstream | 0.32 |
| [[benchmark-suite-builder]] | upstream | 0.26 |
