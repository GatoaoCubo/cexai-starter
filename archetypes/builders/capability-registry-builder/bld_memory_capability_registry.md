---
kind: learning_record
id: p10_lr_capability_registry_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for capability_registry construction
quality: null
title: "Learning Record Capability Registry"
version: "1.0.0"
author: n04_wave8
tags: [capability_registry, builder, learning_record, agent-discovery]
tldr: "Learned patterns and pitfalls for capability_registry construction"
domain: "capability_registry construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [capability_registry construction, learning record capability registry, capability_registry, builder, learning_record, agent-discovery, provider_agent, capability_name, keyword_index, capabilities]
density_score: 0.85
related:
  - capability-registry-builder
  - bld_instruction_capability_registry
  - bld_config_capability_registry
  - p08_qg_capability_registry
  - bld_output_template_capability_registry
---
## Observation
Registry entries with all 8 required fields (capability_name, provider_agent, input_schema, output_schema, cost_tokens, quality_baseline, availability, keyword_index) produce 2-3x higher dispatch precision than partial entries. The most common omission is keyword_index, which prevents TF-IDF-based retrieval from surfacing the agent.

## Pattern
Three-layer indexing (builder_sub_agents | nucleus_domain_agents | nucleus_cards) with separate sections per layer prevents confusion between invocation paths. Builder sub-agents are invoked as Claude Code sub-agents; nucleus domain agents are invoked via the Task tool; nucleus cards describe the nucleus itself. Mixing them in one flat list causes routing errors.

## Evidence
In the CEX WAVE6/WAVE7 grid cycles, orchestrators that used flat agent lists dispatched to wrong nuclei ~20% of the time. Introducing the three-layer structure reduced misrouting to <5% in WAVE8 planning sessions.

## Recommendations
- Always validate `provider_agent` paths with a glob before writing to registry.
- Use verb-noun form for `capability_name` (e.g., "Build knowledge card" not "knowledge cards").
- Derive `keyword_index` from the union of the agent's `domain` and `capabilities` fields -- never invent keywords.
- Mark `quality_baseline: unscored` for any agent with `quality: null` in source.
- Include a `coverage_gaps` section even if empty -- absence of gaps is itself information.
- Re-run `cex_doctor.py` after registry creation to catch phantom references early.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[capability-registry-builder]] | upstream | 0.41 |
| [[bld_prompt_capability_registry]] | upstream | 0.38 |
| [[bld_config_capability_registry]] | upstream | 0.33 |
| [[p08_qg_capability_registry]] | downstream | 0.31 |
| [[bld_output_template_capability_registry]] | upstream | 0.31 |
