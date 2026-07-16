---
kind: collaboration
id: bld_collaboration_planning_strategy
pillar: P12
llm_function: COLLABORATE
purpose: How planning_strategy-builder works in crews with other builders
quality: null
title: "Collaboration Planning Strategy"
version: "1.0.0"
author: wave1_builder_gen
tags: [planning_strategy, builder, collaboration]
tldr: "How planning_strategy-builder works in crews with other builders"
domain: "planning_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [planning_strategy construction, collaboration planning strategy, planning_strategy, builder, collaboration, crew role  
coordinates, receives from, strategy owner, resource manager, risk analyst]
density_score: 0.85
related:
  - bld_collaboration_action_paradigm
  - bld_collaboration_self_improvement_loop
  - bld_collaboration_search_strategy
  - bld_collaboration_reward_model
  - bld_collaboration_sandbox_config
---
## Crew Role  
Coordinates high-level planning steps, aligns team objectives, and defines strategic priorities without executing tasks or reasoning through specifics.  

## Receives From  
| Builder | What | Format |  
|---|---|---|  
| Strategy Owner | Mission goals | JSON |  
| Resource Manager | Availability constraints | CSV |  
| Risk Analyst | Potential obstacles | Text |  
| Stakeholder | Preference inputs | Markdown |  

## Produces For  
| Builder | What | Format |  
|---|---|---|  
| Execution Planner | Prioritized action sequences | YAML |  
| Communication Lead | Summary briefs | PDF |  
| Monitoring System | KPI alignment checklist | JSON |  
| Risk Analyst | Mitigation focus areas | Text |  

## Boundary  
Does NOT handle task execution (workflow_executor), detailed reasoning (reasoning_engine), or real-time data processing (data_pipeline). These are managed by dedicated components.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_action_paradigm]] | sibling | 0.27 |
| [[bld_collaboration_self_improvement_loop]] | sibling | 0.26 |
| [[bld_collaboration_search_strategy]] | sibling | 0.25 |
| [[bld_collaboration_reward_model]] | sibling | 0.24 |
| [[bld_collaboration_sandbox_config]] | sibling | 0.23 |
