---
id: p03_pt_builder_construction
kind: prompt_template
8f: F6_produce
pillar: P03
title: Prompt Template -- Artifact Construction
version: 1.0.0
created: 2026-03-30
updated: 2026-03-30
author: builder_agent
domain: meta-construction
quality: null
tags:
  - "prompt-template"
  - "builder"
  - "N03"
tldr: "F6 PRODUCE template: 9 variables (kind, domain, max_bytes, naming, builder_SP, KC_context, plan, existing_artifacts, open_vars) assembled by the runner into a single LLM call that generates a complete artifact with frontmatter + structured body."
keywords:
  - "kinds_meta.json"
  - "kc library"
  - "llm reasoning"
  - "similarity retriever"
  - "mustache syntax"
  - "artifact scan"
  - "archetypes/builders/{kind}-builder/bld_prompt_{kind}.md"
density_score: 0.88
related:
  - p03_ch_builder_pipeline
  - bld_collaboration_prompt_template
  - bld_knowledge_card_prompt_template
  - p08_ac_builder_nucleus
  - bld_memory_prompt_template
---

# Prompt Template: Artifact Construction

## Usage
Injected at Runner.F6 (PRODUCE). Variables filled by pipeline from F1-F5 outputs.

## Template

```
You are {{builder_system_prompt}}.

TASK: Produce a complete {{kind}} artifact.

CONSTRAINTS (from F1):
- Max bytes: {{max_bytes}}
- Naming: {{naming}}
- Domain: {{domain}}

KNOWLEDGE (from F3):
{{knowledge_context}}

PLAN (from F4):
{{construction_plan}}

EXISTING ARTIFACTS (from F5):
{{existing_artifacts_summary}}

OUTPUT REQUIREMENTS:
1. Start with YAML frontmatter (id, kind, pillar, title, version, created, updated,
   author, quality: null, tags, tldr)
2. Structured markdown body per your output template ISO
3. Use {{open_variables}} for consumer-filled values
4. Density >= 0.85 -- every section must have substantive content
5. Tables for structured data, lists for enumerables, no prose padding
```

## Variables

| Variable | Source | Filled By |
|----------|--------|-----------|
| {{kind}} | resolved from intent | pipeline |
| {{domain}} | User input | pipeline |
| {{max_bytes}} | kinds_meta.json | F1 |
| {{naming}} | kinds_meta.json | F1 |
| {{builder_system_prompt}} | builder ISOs | F2 |
| {{knowledge_context}} | KC library | F3 |
| {{construction_plan}} | LLM reasoning | F4 |
| {{existing_artifacts_summary}} | artifact scan | F5 |
| {{open_variables}} | mustache syntax | consumer at use-time |

## Variable Resolution Order

The Runner fills variables in a strict order to avoid circular dependencies:

| Phase | Variables Filled | Source |
|-------|-----------------|--------|
| F1 | kind, domain, max_bytes, naming | kinds_meta.json + _schema.yaml |
| F2 | builder_system_prompt | archetypes/builders/{kind}-builder/bld_prompt_{kind}.md |
| F3 | knowledge_context | KC library + retriever similarity scan |
| F4 | construction_plan | LLM call with F1+F2+F3 outputs |
| F5 | existing_artifacts_summary | similarity retriever top-5 matches |
| Runtime | open_variables | Consumer fills at use-time (not the builder nucleus) |

## Token Budget Allocation

Total budget for F6 PRODUCE call: ~4000 output tokens (configurable).

| Section | Target Allocation | Notes |
|---------|------------------|-------|
| Frontmatter | ~200 tokens | Fixed overhead, rarely varies |
| Body sections | ~3000 tokens | Scales with kind complexity |
| Tables/code | ~800 tokens | Higher density per token than prose |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ch_builder_pipeline]] | related | 0.45 |
| [[bld_collaboration_prompt_template]] | related | 0.30 |
| [[bld_knowledge_card_prompt_template]] | upstream | 0.29 |
| [[p08_ac_builder_nucleus]] | downstream | 0.29 |
| [[bld_memory_prompt_template]] | downstream | 0.27 |
