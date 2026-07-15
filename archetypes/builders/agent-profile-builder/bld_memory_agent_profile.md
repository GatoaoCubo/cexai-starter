---
kind: learning_record
id: p10_lr_agent_profile_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for agent_profile construction
quality: null
title: "Learning Record Agent Profile"
version: "1.0.0"
author: wave1_builder_gen
tags: [agent_profile, builder, learning_record]
tldr: "Learned patterns and pitfalls for agent_profile construction"
domain: "agent_profile construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [agent_profile construction, learning record agent profile, agent_profile, builder, learning_record, observation
common, pattern
effective, evidence
reviewed, related artifacts, traits]
density_score: 0.85
related:
  - agent-profile-builder
  - bld_knowledge_card_agent_profile
  - bld_collaboration_agent_profile
  - p10_lr_judge_config_builder
  - p10_mem_eval_metric_builder
---
## Observation
Common issues include inconsistent trait definitions, overgeneralization of roles, and misalignment between persona goals and use cases. Profiles often lack specificity, leading to ambiguous or unrealistic agent identities.

## Pattern
Effective profiles use concise, role-specific traits tied to clear objectives. They balance uniqueness with relatability, ensuring consistency across interactions and contextual adaptability.

## Evidence
Reviewed artifacts showed success when personas included 3-5 distinct, actionable traits aligned with defined scenarios (e.g., "conflict resolver" with "empathetic listener" trait).

## Recommendations
- Align persona traits directly with the agent’s primary use case and interaction scope.
- Use consistent language to avoid contradictions in identity (e.g., avoid mixing "authoritative" and "collaborative" unless contextually justified).
- Limit traits to 5-7 to maintain clarity and prevent dilution of identity.
- Test personas against edge cases to ensure coherence under varied scenarios.
- Document persona boundaries explicitly to guide behavior and avoid overreach.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[agent-profile-builder]] | upstream | 0.36 |
| [[bld_knowledge_agent_profile]] | upstream | 0.34 |
| [[bld_orchestration_agent_profile]] | downstream | 0.26 |
| p10_lr_judge_config_builder | sibling | 0.23 |
| [[p10_mem_eval_metric_builder]] | related | 0.22 |
