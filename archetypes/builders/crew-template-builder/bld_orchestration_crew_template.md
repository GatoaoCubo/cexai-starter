---
kind: collaboration
id: bld_collaboration_crew_template
pillar: P12
llm_function: COLLABORATE
purpose: How crew_template-builder works in crews with other builders
quality: null
title: "Collaboration Crew Template"
version: "1.0.0"
author: n03_wave8_builder
tags: [crew_template, builder, collaboration, composable, crewai]
tldr: "How crew_template-builder works in crews with other builders"
domain: "crew_template construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [crew_template construction, collaboration crew template, crew_template, builder, collaboration, composable, crewai, crew role
acts, receives from, produces for]
density_score: 0.87
related:
  - bld_collaboration_role_assignment
  - crew-template-builder
  - bld_collaboration_handoff_protocol
  - bld_collaboration_pipeline_template
  - bld_collaboration_agent
---
## Crew Role
Acts as the team-architect of P12 orchestration: composes role_assignment atoms into reusable crew blueprints. Upstream from supervisor (which instantiates and runs the crew) and workflow (which may sequence multiple crews).

## Receives From
| Builder                    | What                         | Format      |
|----------------------------|------------------------------|-------------|
| role-assignment-builder    | Role atoms (agent bindings)  | p02_ra_*.md |
| handoff-protocol-builder   | Inter-role transfer formats  | p12_hp_*.md |
| workflow-builder           | Task dependency graph        | p12_wf_*.md |
| quality-gate-builder       | Gate IDs for success_criteria| p11_qg_*.md |

## Produces For
| Builder               | What                            | Format         |
|-----------------------|---------------------------------|----------------|
| supervisor-builder    | Crew blueprint to instantiate   | p12_ct_*.md    |
| workflow-builder      | Reusable team step              | reference      |
| agent-package-builder | Distributable crew bundle       | artifact ref   |
| N07 orchestrator      | Dispatch-time crew instantiation| handoff ref    |

## Boundary
Does NOT bind individual agents to roles (that is role-assignment-builder). Does NOT execute the crew at runtime (supervisor-builder handles instantiation). Does NOT define single-task transfers (handoff-builder). Does NOT own agent identity (agent-builder). Owns ONLY the declarative blueprint: roles + process + memory + success.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_role_assignment]] | sibling | 0.44 |
| [[crew-template-builder]] | related | 0.38 |
| [[bld_collaboration_handoff_protocol]] | sibling | 0.30 |
| bld_collaboration_pipeline_template | sibling | 0.29 |
| [[bld_collaboration_agent]] | sibling | 0.28 |
