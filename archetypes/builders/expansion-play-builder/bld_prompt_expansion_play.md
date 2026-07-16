---
kind: instruction
id: bld_instruction_expansion_play
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for expansion_play
quality: null
title: "Instruction Expansion Play"
version: "1.0.0"
author: wave6_n06
tags: [expansion_play, builder, instruction, upsell, NRR, QBR]
tldr: "Step-by-step production process for expansion_play"
domain: "expansion_play construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [expansion_play construction, instruction expansion play, expansion_play, builder, instruction, upsell, related artifacts, upsell triggers, attach rate, talk track]
density_score: 0.85
related:
  - expansion-play-builder
  - bld_knowledge_card_expansion_play
  - bld_output_template_expansion_play
  - p10_mem_expansion_play_builder
  - bld_schema_expansion_play
---
## Phase 1: RESEARCH
1. Identify the target account segment (SMB/MM/ENT) and current ARR band.
2. Extract product usage signals: active seats vs. licensed seats, feature adoption rate, usage velocity (WAU/MAU).
3. Map upsell triggers: seat threshold (>80% utilization), feature unlock events, integration milestones.
4. Identify cross-sell adjacency: which add-on SKUs have highest attach rate for this segment?
5. Review NRR benchmarks: current account NRR vs. target >120%.
6. Pull QBR history: last expansion conversation, customer health score, champion strength.

## Phase 2: COMPOSE
1. Reference bld_schema_expansion_play.md for required fields (account_id, trigger_type, expansion_type, NRR_target).
2. Define the expansion motion: seat upsell, tier upgrade, add-on cross-sell, or usage-based ramp.
3. Write the AE/CSM talk track: value narrative, business case, ROI calculation.
4. Set trigger thresholds and automation rules (e.g., alert when seat utilization > 80% for 14 days).
5. Build the account mapping: economic buyer, champion, expansion blocker, procurement contact.
6. Define the QBR slide structure: current value delivered, expansion opportunity, success metrics.
7. Set NRR contribution calculation: expansion ARR / beginning ARR * 100.
8. Add objection handling: budget freeze, contract timing, competing priorities.
9. Define success criteria and follow-up cadence post-expansion conversation.

## Phase 3: VALIDATE
- [ ] Upsell triggers are quantified (not vague -- e.g., "> 80% seat utilization for 14 days").
- [ ] NRR model includes expansion, contraction, and churn components.
- [ ] Talk track has opening hook, value statement, ask, and next step.
- [ ] Account map covers economic buyer and champion (minimum 2 stakeholders).
- [ ] QBR structure maps to customer success metrics, not internal metrics.
- [ ] Cross-sell play references specific SKU and attach rate data.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[expansion-play-builder]] | related | 0.60 |
| [[bld_knowledge_card_expansion_play]] | upstream | 0.58 |
| [[bld_output_template_expansion_play]] | downstream | 0.46 |
| [[p10_mem_expansion_play_builder]] | downstream | 0.44 |
| [[bld_schema_expansion_play]] | downstream | 0.44 |
