---
id: kc_dual_loop_architecture
kind: knowledge_card
8f: F3_inject
title: Dual Loop Architecture
version: 1.0.0
quality: null
pillar: P01
tldr: "Control framework combining strategic outer loop with operational inner loop and feedback"
when_to_use: "When a system needs hierarchical coordination with separate strategic and operational layers"
keywords: [task decomposition, priority ranking, cross-loop communication, real-time decision-making, error detection and correction, adaptive behavior adjustment, subtask execution, sensor data]
density_score: 0.97
related:
  - dual-loop-architecture-builder
  - bld_knowledge_card_dual_loop_architecture
  - bld_collaboration_dual_loop_architecture
  - p10_lr_dual_loop_architecture_builder
  - bld_instruction_dual_loop_architecture
---

# Dual Loop Architecture

## Overview
The dual loop architecture is a control framework combining an outer loop for strategic coordination and an inner loop for operational execution. This structure enables adaptive task management through hierarchical decision-making and real-time feedback.

## Outer Loop (Strategic)
- **Function**: Coordinates high-level goals, resource allocation, and long-term planning
- **Characteristics**: 
  - Task decomposition
  - Priority ranking
  - Cross-loop communication
- **Examples**: 
  - Decomposing complex missions into subtasks
  - Monitoring system-wide performance metrics

## Inner Loop (Operational)
- **Function**: Executes specific tasks with immediate feedback mechanisms
- **Characteristics**: 
  - Real-time decision-making
  - Error detection and correction
  - Adaptive behavior adjustment
- **Examples**: 
  - Implementing subtask execution
  - Applying corrective actions based on sensor data

## Interaction Pattern
1. The outer loop defines objectives and parameters
2. The inner loop executes operations and gathers feedback
3. Feedback is used to refine outer loop strategies
4. This cycle continues until the mission is complete

## Key Benefits
- Enables complex problem-solving through layered control
- Facilitates efficient resource utilization
- Supports continuous improvement through feedback loops
- Maintains system stability while adapting to changing conditions

## How to use

```text
ROLE: you are architecting a system that needs separate strategic and operational control.
1. Assign the outer loop: goals, resource allocation, task decomposition, priority ranking.
2. Assign the inner loop: subtask execution, real-time decisions, error detection + correction.
3. Wire the Interaction Pattern: outer sets objectives -> inner executes + gathers feedback -> refine.
4. Map this onto CEX: N07 is the outer loop; dispatched nuclei are the inner loop.
Primary 8F verb: INJECT (reference consumed at F3 when designing hierarchical coordination).
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[dual-loop-architecture-builder]] | downstream | 0.57 |
| [[bld_knowledge_card_dual_loop_architecture]] | sibling | 0.57 |
| [[bld_collaboration_dual_loop_architecture]] | downstream | 0.56 |
| [[p10_lr_dual_loop_architecture_builder]] | downstream | 0.49 |
| [[bld_instruction_dual_loop_architecture]] | downstream | 0.47 |
