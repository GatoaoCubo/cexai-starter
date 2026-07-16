---
quality: null
quality: null
kind: collaboration
id: bld_collaboration_pipeline_template
pillar: P12
llm_function: COLLABORATE
purpose: How pipeline_template-builder works with other builders
title: "Collaboration Pipeline Template"
version: "1.0.0"
author: n03_builder
tags: [pipeline_template, builder, collaboration, scenario_indexed]
tldr: "How pipeline_template-builder works with other builders"
domain: "pipeline_template construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F8_collaborate"
keywords: [pipeline_template construction, collaboration pipeline template, pipeline_template, builder, collaboration, scenario_indexed, builder role
acts, receives from, produces for]
density_score: 0.87
related:
 - pipeline-template-builder
 - bld_architecture_pipeline_template
---
## Builder Role
Acts as the scenario-recipe encoder of P12 orchestration: translates a software engineering task type into a deterministic stage sequence with mandatory quality gates. Upstream from supervisor (which instantiates and runs the pipeline) and downstream from role_assignment (which binds agents to stage roles).

## Receives From
| Builder | What | Format |
|---------------------------|--------------------------------|-------------|
| role-assignment-builder | Stage role agent bindings | p02_ra_*.md |
| workflow-builder | Complex branching when needed | p12_wf_*.md |
| quality-gate-builder | Gate IDs for quality_gates | p11_qg_*.md |
| team_charter-builder | Mission scope + task context | p12_tc_*.md |

## Produces For
| Builder | What | Format |
|-----------------------|-----------------------------------------|----------------|
| supervisor-builder | Pipeline recipe to instantiate | p12_pt_*.yaml |
| workflow-builder | Named pipeline step reference | reference |
| agent-package-builder | Distributable pipeline bundle | artifact ref |
| N07 orchestrator | Dispatch-time pipeline instantiation | handoff ref |

## Boundary
Does NOT compose multi-role teams with topology (crew_template handles that). Does NOT define arbitrary DAGs with conditional branches (workflow/dag). Does NOT define a single execution step (workflow_node). Does NOT execute pipelines at runtime (supervisor). Owns ONLY the declarative scenario recipe: scenario -> ordered stages -> revision loop -> quality gates.

## Interaction with crew_template
pipeline_template and crew_template are complementary, not competing:
- crew_template answers "WHO works together and HOW they coordinate" (team blueprint).
- pipeline_template answers "WHAT stages execute in WHAT order for WHAT scenario" (recipe).
A crew_template CAN reference pipeline_template stages as its process specification.
A pipeline_template CAN be instantiated within a crew_template as the coordination script.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[pipeline-template-builder]] | related | 0.31 |
| [[bld_architecture_pipeline_template]] | upstream | 0.30 |
