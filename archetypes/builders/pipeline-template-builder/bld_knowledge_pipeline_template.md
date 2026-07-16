---
quality: null
quality: null
kind: knowledge_card
id: bld_knowledge_card_pipeline_template
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for pipeline_template production
title: "Knowledge Card Pipeline Template"
version: "1.0.0"
author: n03_builder
tags: [pipeline_template, builder, knowledge_card, scenario_indexed]
tldr: "Domain knowledge for pipeline_template production"
domain: "pipeline_template construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F3_inject"
keywords: [pipeline_template construction, knowledge card pipeline template, pipeline_template, builder, knowledge_card, scenario_indexed, domain overview
pipeline, canonical scenarios]
density_score: 0.88
related:
 - pipeline-template-builder
 - n00_pipeline_template_manifest
 - kc_pipeline_template
 - p11_qg_pipeline_template
 - pipeline_template_n03
---
## Domain Overview
Pipeline templates encode multi-agent scenario-indexed agent sequences for software engineering tasks. Where crew_template defines a reusable TEAM (fixed roles + topology), pipeline_template defines a reusable RECIPE (scenario -> ordered stages -> revision loop). The pattern originates from multi-agent-pattern: 7 canonical scenarios with mandatory @reviewer + @tester gates and max 3 revision iterations. Priority order enforces security concerns over quality over implementation details.

## 7 Canonical Scenarios
| Scenario | Stage Sequence | Notes |
|----------|----------------|-------|
| new_feature | finder -> analyst -> architect -> planner -> coder -> reviewer -> tester -> documenter | Full feature lifecycle |
| new_feature_security | finder -> researcher -> analyst -> architect -> planner -> coder -> security -> reviewer -> tester -> documenter | Adds researcher + security pre-tester |
| bug_fix_unknown | finder -> debugger -> fixer -> reviewer -> tester | Unknown root cause: debug phase required |
| bug_fix_known | finder -> fixer -> reviewer -> tester | Known cause: skip debug, direct fix |
| refactoring | finder -> analyst -> refactorer -> reviewer -> tester | Structural improvement, no behavior change |
| perf_opt | finder -> analyst -> optimizer -> reviewer -> tester | Performance bottleneck removal |
| infra | finder -> devops -> reviewer -> tester | Infrastructure/config/CI changes |

## Canonical Role Definitions
| Role | Responsibility | Model Tier |
|------|---------------|-----------|
| finder | Locates relevant code/files for the task | medium |
| analyst | Analyzes code structure and impact | high |
| architect | Designs system-level solution | xhigh |
| planner | Breaks solution into implementation steps | xhigh |
| coder | Implements code changes | high |
| refactorer | Restructures code without behavior change | high |
| optimizer | Removes performance bottlenecks | high |
| debugger | Traces root cause of bugs | high |
| fixer | Applies targeted patch | high |
| devops | Modifies infra/CI/CD/config | high |
| documenter | Updates docs and comments | medium |
| reviewer | Code quality + diff review | medium |
| tester | Runs/writes regression tests | low |
| researcher | Gathers background knowledge | medium |
| security | Security vulnerability review | medium |

## Key Concepts
| Concept | Definition | Source |
|---------|------------|--------|
| Scenario | Engineering task type that determines stage sequence | multi-agent |
| Stage | Single-role execution step in pipeline order | multi-agent |
| Revision Loop | Max-bounded retry cycle when gate fails | multi-agent |
| Quality Gate | Mandatory reviewer+tester pair; must pass to proceed | multi-agent |
| Priority Order | security > quality > implementation | multi-agent |
| Model Tier | Cognitive load category (low/medium/high/xhigh) -> LLM model selection | CEX routing |

## Boundary vs Related Kinds
| Kind | Difference |
|------|-----------|
| crew_template | Fixed multi-role TEAM blueprint with topology (sequential/hierarchical/consensus). Pipeline is a scenario RECIPE with linear stages. |
| workflow | Arbitrary DAG with conditional branches and parallel execution. Pipeline is a predefined linear recipe. |
| workflow_node | Single step in a workflow or pipeline. Pipeline_template is the entire flow. |
| dag | Dependency graph without execution semantics. Pipeline encodes execution order + gates. |

## Industry Context
multi-agent (2025) is the reference implementation of scenario-indexed multi-agent coding pipelines. The 7-scenario catalog maps to aider.chat task modes, Codex CLI task types, and Claude Code /build patterns. The revision-loop pattern is adopted by SWE-bench-style agent evaluations as the standard for iterative code repair.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[pipeline-template-builder]] | downstream | 0.64 |
| [[n00_pipeline_template_manifest]] | sibling | 0.62 |
| [[kc_pipeline_template]] | sibling | 0.60 |
| [[p11_qg_pipeline_template]] | downstream | 0.55 |
| [[pipeline_template_n03]] | downstream | 0.54 |
