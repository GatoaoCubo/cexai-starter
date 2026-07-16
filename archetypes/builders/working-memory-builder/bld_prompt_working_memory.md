---
quality: null
quality: null
kind: instruction
id: bld_instruction_working_memory
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for working_memory
pattern: 3-phase pipeline (scope -> compose -> validate)
title: "Instruction Working Memory"
version: "1.0.0"
author: n03_builder
tags:
  - "working_memory"
  - "builder"
  - "instruction"
tldr: "3-phase process: scope the task and context slots, compose with expiry and clear policy, validate gates."
domain: "working memory construction"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F6_produce"
keywords:
  - "working memory construction"
  - "instruction working memory"
  - "phase process"
  - "validate gates"
  - "working_memory"
  - "builder"
  - "instruction"
  - "{{vars}}"
  - "^p10_wm_[a-z][a-z0-9_]+$"
  - "write overview"
density_score: 0.90
related:
  - working-memory-builder
  - p10_qg_working_memory
  - bld_schema_working_memory
  - bld_output_template_working_memory
  - p01_kc_working_memory
---
# Instructions: How to Produce a working_memory

## Phase 1: SCOPE
1. Identify the task: what specific in-flight task this memory serves (task_id)
2. List required context slots: what intermediate state does the task need to hold?
   (e.g., current_step, accumulated_results, error_count, intermediate_data)
3. Determine capacity_limit: max tokens or slot count to prevent unbounded growth
4. Set expiry: TTL in seconds/minutes, or "on_task_complete" trigger
5. Define clear_on_complete policy: what happens when task finishes
   - CLEAR: wipe all slots (ephemeral use case)
   - PROMOTE: move key slots to entity_memory or episodic_memory before clearing
6. Identify any slots that should survive task completion (candidates for promotion)
7. Check for existing working_memory artifacts with overlapping task_id

## Phase 2: COMPOSE
1. Read SCHEMA.md -- source of truth for all fields
2. Read OUTPUT_TEMPLATE.md -- fill `{{vars}}` following SCHEMA constraints
3. Fill frontmatter: all required fields (quality: null)
4. Write context_slots: typed key-value schema for each slot
5. Declare capacity_limit with unit (tokens or slots)
6. Write expiry policy (TTL or task-triggered)
7. Write clear_on_complete with promotion targets if any
8. Write Overview: what task this memory serves, why it needs working memory
9. Write Context Slots: table of slot name, type, purpose, example value
10. Verify body <= 3072 bytes

## Phase 3: VALIDATE
1. Check QUALITY_GATES.md -- verify each HARD gate manually
2. Confirm id matches `^p10_wm_[a-z][a-z0-9_]+$`
3. Confirm kind == working_memory
4. Confirm task_id is declared and non-empty
5. Confirm context_slots has >= 1 slot defined
6. Confirm expiry is declared (TTL or trigger)
7. Cross-check: no long-term facts (those belong in entity_memory), no session persistence (session_state), no past episodes (episodic_memory)
8. Revise if score < 8.0 -- most common fix: add slot type annotations or clear_on_complete policy

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[working-memory-builder]] | downstream | 0.49 |
| [[p10_qg_working_memory]] | downstream | 0.47 |
| [[bld_schema_working_memory]] | downstream | 0.42 |
| [[bld_output_template_working_memory]] | downstream | 0.40 |
| [[p01_kc_working_memory]] | downstream | 0.39 |
