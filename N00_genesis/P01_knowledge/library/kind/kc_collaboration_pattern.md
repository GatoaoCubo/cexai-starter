---
id: kc_collaboration_pattern
kind: knowledge_card
8f: F3_inject
title: Collaboration Pattern
version: 1.0.0
quality: null
pillar: P01
tldr: "Structural framework for multi-agent coordination: centralized, decentralized, hierarchical, or P2P"
when_to_use: "When designing how multiple agents communicate, delegate tasks, and resolve conflicts"
keywords: [multi-agent coordination, task delegation, conflict resolution, information sharing topologies, swarm intelligence, blockchain consensus mechanisms, fault tolerance mechanisms, scalability constraints, security protocols]
density_score: 1.0
related:
  - p01_kc_multi_agent_orchestration_patterns
  - bld_knowledge_card_collaboration_pattern
  - collaboration-pattern-builder
  - bld_memory_collaboration_pattern
  - bld_instruction_collaboration_pattern
---

# Collaboration Pattern

A collaboration pattern defines the structural framework for multi-agent coordination. It establishes:
- Communication protocols
- Task delegation rules
- Conflict resolution mechanisms
- Information sharing topologies

## Core Patterns

1. **Centralized Control**
   - Single orchestrator coordinates all agents
   - Centralized decision-making
   - Example: Task assignment via master-worker architecture

2. **Decentralized Coordination**
   - Agents self-organize through local interactions
   - Emergent behavior from simple rules
   - Example: Swarm intelligence in robotics

3. **Hierarchical Structure**
   - Nested layers of control and execution
   - Clear command chains and subordination
   - Example: Military operation command structures

4. **Peer-to-Peer Network**
   - Equal agent participation
   - Distributed decision-making
   - Example: Blockchain consensus mechanisms

## Key Considerations
- Synchronization requirements
- Fault tolerance mechanisms
- Scalability constraints
- Security protocols for collaborative workflows

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_collaboration_pattern]] | sibling | 0.29 |
| [[collaboration-pattern-builder]] | downstream | 0.29 |
| [[bld_memory_collaboration_pattern]] | downstream | 0.27 |
| [[bld_instruction_collaboration_pattern]] | downstream | 0.26 |
