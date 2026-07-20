---
id: kc_action_paradigm
kind: knowledge_card
8f: F3_inject
title: Action Paradigm
version: 1.0.0
quality: null
pillar: P01
tldr: "Framework defining how agents execute actions, make decisions, and interact with environments"
when_to_use: "When designing agent behavior models for task execution and environment interaction"
keywords: [action execution models, reactive decision-making, iterative refinement, sensor input processing, actuator output execution, feedback loop integration, precondition validation, post-action evaluation, error recovery mechanisms]
density_score: 0.99
related:
  - bld_instruction_action_paradigm
  - bld_knowledge_card_action_paradigm
  - action-paradigm-builder
  - bld_memory_action_paradigm
  - bld_collaboration_action_prompt
---

# Action Paradigm: How Agents Execute Actions in Environments

This knowledge card defines the framework agents use to perform tasks, make decisions, and interact with their environment. The paradigm encompasses:

1. **Action Execution Models**  
   - Procedural execution (step-by-step task breakdown)  
   - Reactive decision-making (environment-driven responses)  
   - Iterative refinement (adaptive improvement cycles)  

2. **Environment Interaction**  
   - Sensor input processing  
   - Actuator output execution  
   - Feedback loop integration  

3. **Task Completion Protocols**  
   - Precondition validation  
   - Post-action evaluation  
   - Error recovery mechanisms  

The paradigm ensures agents can adapt to dynamic environments, handle uncertainties, and optimize resource usage. Key components include:  
- Action prioritization frameworks  
- Context-aware execution contexts  
- Performance feedback integration  

Examples:  
- Procedural execution in manufacturing workflows  
- Reactive decision-making in real-time systems  
- Iterative refinement in creative problem-solving  

This concept is foundational for understanding agent behavior in complex systems and environment interaction patterns.

## How to use

```text
ROLE: you are designing an agent's action-execution behavior model.
1. Choose an execution model (procedural, reactive, or iterative) for the task class.
2. Define the environment interaction loop: sensor input -> decision -> actuator output -> feedback.
3. Add task-completion protocols: precondition validation, post-action evaluation, error recovery.
4. Wire action prioritization + context-aware execution + performance feedback.
Primary 8F verb: INJECT (foundational reference consumed at F3 when modeling agent behavior).
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_action_paradigm]] | downstream | 0.36 |
| [[bld_knowledge_card_action_paradigm]] | sibling | 0.35 |
| [[action-paradigm-builder]] | downstream | 0.35 |
| [[bld_memory_action_paradigm]] | downstream | 0.28 |
| [[bld_collaboration_action_prompt]] | downstream | 0.23 |
