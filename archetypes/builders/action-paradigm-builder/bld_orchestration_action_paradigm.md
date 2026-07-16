---
kind: collaboration
id: bld_collaboration_action_paradigm
pillar: P12
llm_function: COLLABORATE
purpose: How action_paradigm-builder works in crews with other builders
quality: null
title: "Collaboration Action Paradigm"
version: "1.0.0"
author: wave1_builder_gen
tags: [action_paradigm, builder, collaboration]
tldr: "How action_paradigm-builder works in crews with other builders"
domain: "action_paradigm construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [action_paradigm construction, collaboration action paradigm, action_paradigm, builder, collaboration, crew role
orchestrates, receives from, task planner, produces for, boundary
does]
density_score: 0.85
related:
  - bld_collaboration_collaboration_pattern
  - bld_collaboration_self_improvement_loop
  - bld_collaboration_thinking_config
  - bld_collaboration_prompt_technique
  - bld_collaboration_visual_workflow
---
## Crew Role
Orchestrates action execution workflows, decomposing high-level goals into executable steps, ensuring alignment with domain constraints and resource availability.

## Receives From
| Builder       | What               | Format      |
|---------------|--------------------|-------------|
| Task Planner  | Goal definitions   | JSON        |
| ResourceMgr   | Available resources| YAML        |
| Validator     | Constraint rules   | Structured  |
| Monitor       | Status updates     | JSON        |

## Produces For
| Builder       | What               | Format      |
|---------------|--------------------|-------------|
| Executor      | Action plan        | JSON        |
| Logger        | Execution logs     | YAML        |
| FeedbackSys   | Completion signals | Structured  |
| ErrorHandler  | Failure reports    | JSON        |

## Boundary
Does NOT execute actions directly (handled by cli_tool/api_client builders), manage user interfaces
(handled by agent_computer_interface builder), or handle sequential task ordering (handled by
workflow builder).

## Properties

| Property | Value |
|----------|-------|
| Kind | `collaboration` |
| Pillar | P12 |
| Domain | action_paradigm construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_collaboration_pattern]] | sibling | 0.31 |
| [[bld_collaboration_self_improvement_loop]] | sibling | 0.28 |
| [[bld_collaboration_thinking_config]] | sibling | 0.26 |
| [[bld_collaboration_prompt_technique]] | sibling | 0.25 |
| [[bld_collaboration_visual_workflow]] | sibling | 0.24 |
