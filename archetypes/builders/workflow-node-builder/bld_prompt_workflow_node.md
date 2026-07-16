---
kind: instruction
id: bld_instruction_workflow_node
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for workflow_node
quality: null
title: "Instruction Workflow Node"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [workflow_node, builder, instruction]
tldr: "Step-by-step production process for workflow_node"
domain: "workflow_node construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [workflow_node construction, instruction workflow node, workflow_node, builder, instruction, related artifacts, input output, error handling, sibling, schema]
density_score: 0.85
related:
  - workflow-node-builder
  - bld_instruction_visual_workflow
  - bld_collaboration_workflow_node
  - n00_workflow_node_manifest
  - visual-workflow-builder
---
## Phase 1: RESEARCH  
1. Analyze schema requirements from SCHEMA.md for node typing rules  
2. Identify required input/output ports and their data types  
3. Review existing workflow_node implementations in P12 pillar  
4. Document visual representation standards (colors, icons, connectors)  
5. Study error handling patterns in workflow_node lifecycle methods  
6. Map node behavior to programmatic execution flow diagrams  

## Phase 2: COMPOSE  
1. Create node class with typed identifier per SCHEMA.md  
2. Implement port definitions using OUTPUT_TEMPLATE.md structure  
3. Write initialization method for visual configuration  
4. Code execution logic with input/output validation  
5. Add error propagation handlers for failure states  
6. Implement serialization methods for workflow storage  
7. Integrate with UI framework for drag-and-drop placement  
8. Write unit tests for edge case scenarios  
9. Finalize documentation in node's metadata block  

## Phase 3: VALIDATE  
[ ] [ ] Verify schema compliance with SCHEMA.md  
[ ] [ ] Test port type mismatches in execution  
[ ] [ ] Confirm visual rendering matches design specs  
[ ] [ ] Validate error handling in all lifecycle stages  
[ ] [ ] Ensure compatibility with P12 workflow engine

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[workflow-node-builder]] | downstream | 0.47 |
| [[bld_instruction_visual_workflow]] | sibling | 0.40 |
| [[bld_collaboration_workflow_node]] | downstream | 0.37 |
| [[n00_workflow_node_manifest]] | downstream | 0.33 |
| [[visual-workflow-builder]] | downstream | 0.32 |
