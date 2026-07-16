---
id: p01_kc_skill
kind: knowledge_card
type: kind
pillar: P04
title: "Skill — Deep Knowledge for skill"
version: 1.0.0
created: 2026-04-02
updated: 2026-04-02
author: builder_knowledge
domain: skill
quality: null
tags: [skill, p04, reusable, kind-kc]
tldr: "Reusable capability with structured phases, triggers, and lifecycle management for repeatable workflows"
when_to_use: "Building, reviewing, or reasoning about skill artifacts"
keywords: [skill, phases, trigger, reusable, capability, workflow, lifecycle]
feeds_kinds: [skill]
8f: "F3_inject"
density_score: null
llm_function: REASON
related:
  - plugin-builder
  - bld_prompt_synthetic_data_config
  - bld_prompt_query_optimizer
---
# Skill

This ISO defines a plugin contract: the extension surface a host uses to load, register, and invoke external capability.

## Spec
```yaml
kind: skill
pillar: P04
llm_function: TOOL
max_bytes: 4096
naming: p04_skill_{{name}}.md + .yaml
core: true

## Token Budget

| Component | Allocation | Notes |
|-----------|-----------|-------|
| System prompt | 15%% | Builder identity + sin lens |
| Context (ISOs) | 40%% | 12 ISOs loaded per builder |
| Domain knowledge | 25%% | KCs + examples + memory |
| Generation headroom | 20%% | Artifact output space |

## Style Constraints

| Dimension | Guideline |
|-----------|-----------|
| Voice | Technical, precise, builder-appropriate |
| Structure | Tables over prose; data over description |
| Density | >= 0.85; every sentence adds information |
| References | Use canonical kind names, not synonyms |

## Properties

| Property | Value |
|----------|-------|
| Kind | `prompt` |
| Pillar | P03 |
| Domain | plugin construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_plugin]] | related | 0.30 |
| [[plugin-builder]] | related | 0.28 |
| [[bld_prompt_synthetic_data_config]] | upstream | 0.27 |
| [[n00_plugin_manifest]] | sibling | 0.26 |
| [[bld_prompt_query_optimizer]] | upstream | 0.26 |
