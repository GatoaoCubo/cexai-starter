---
id: kc_crew_template
kind: knowledge_card
8f: F3_inject
title: Crew Template
version: 1.0.0
quality: null
pillar: P01
tldr: "Reusable blueprint defining multi-role crew structure with process topology and handoff protocol"
when_to_use: "When a deliverable requires coordinated handoffs between multiple specialized roles"
keywords: [template_id, crew_name, roles, process, memory, success_criteria, quality_gate, dependencies, validation phases, trigger conditions]
density_score: 0.98
---

# Crew Template

A reusable blueprint for defining crew structures that bridges GDP decisions (WHAT) to autonomous execution (HOW). Key components:

## Core Structure
- **template_id**: Unique identifier for the template
- **crew_name**: Human-readable name for the crew
- **roles**: List of roles with responsibilities and skills
- **process**: Workflow definition with sequential/hierarchical steps
- **memory**: Memory management system for context retention
- **success_criteria**: Clear indicators for successful mission completion
- **quality_gate**: Reference to associated quality gate configuration
- **dependencies**: External systems or data sources required

## Example Roles
| Role | Responsibilities | Skills |
|------|------------------|--------|
| Planner | Define objectives, allocate resources | Strategic thinking, resource management |
| Executor | Carry out tasks, monitor progress | Task execution, problem-solving |
| Validator | Assess quality, ensure compliance | Critical thinking, quality assurance |
| Communicator | Maintain stakeholder engagement | Interpersonal skills, communication |

## Quality Integration
- **Validation Phases**: Must include at least the `validate`, `score`, and `approve` phases from the quality gate framework
- **Trigger Conditions**: Should align with quality gate trigger types (user_invocable, agent_only)
- **Metrics**: Include success metrics that feed into quality scoring systems

## Implementation Notes
- Templates should be versioned with semantic versioning (e.g., `v1.0.0`)
- Include a `quality_gate` field referencing the associated quality gate configuration
- Ensure memory systems support the required context retention for validation phases
- Define clear success criteria that align with quality gate thresholds

## How to use

You are assembling a crew. Read this card at **F2 BECOME / F3 INJECT**, then
author the three WAVE8 artifacts it describes.

1. Pick the process topology: sequential, hierarchical, or consensus.
2. Write one `role_assignment` per role (binds role_name -> agent_id).
3. Reference them in the `crew_template` Roles table with the chosen process.
4. Write a `team_charter` with mission, budget, deadline, and quality gate.
5. Validate with `python _tools/cex_crew.py show {name}` before running.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_collaboration_quality_gate | downstream | 0.21 |
| p01_kc_steps | sibling | 0.20 |
| [[bld_orchestration_crew_template]] | downstream | 0.19 |
| p01_kc_skill | sibling | 0.19 |
