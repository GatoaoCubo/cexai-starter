---
kind: tools
id: bld_tools_instruction
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for instruction production
quality: null
title: "Tools Instruction"
version: "1.0.0"
author: n03_builder
tags: [instruction, builder, examples]
tldr: "Golden and anti-examples for instruction construction, demonstrating ideal structure and common pitfalls."
domain: "instruction construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [instruction construction, tools instruction, instruction, builder, examples, production tools, data sources, tool permissions, interim validation
no, pipeline integration]
density_score: 0.90
related:
  - bld_tools_action_prompt
  - bld_tools_prompt_version
  - bld_tools_retriever_config
  - bld_tools_constraint_spec
  - bld_tools_memory_scope
---

# Tools: instruction-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing instructions in pool | Phase 1 (check duplicates) | CONDITIONAL |
| validate_artifact.py | Generic artifact validator | Phase 3 | [PLANNED] |
| cex_forge.py | Generate artifact from seeds | Alternative compose | [PLANNED] |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P03_prompt/_schema.yaml | Field definitions, kinds |
| CEX Examples | P03_prompt/examples/ | Real instruction artifacts |
| ISO Instructions | records/agents/*/agent_package/ISO_*_INSTRUCTIONS.md | 213 existing instructions |
| Handoff files | .claude/handoffs/*.md | 255 operational handoffs (instruction-like) |
| SEED_BANK | archetypes/SEED_BANK.yaml | Seeds for P03_instruction |
| TAXONOMY | archetypes/TAXONOMY_LAYERS.yaml | Layer position, overlaps |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
No automated validator exists yet. Manually check each QUALITY_GATES.md gate against
the produced artifact. Key checks: YAML parses, id pattern, steps_count match,
one action per step, prerequisites are verifiable, no identity/persona content.

## Pipeline Integration

1. Created via 8F pipeline from F1-Focus through F8-Furnish
2. Scored by cex_score across three structural layers
3. Compiled by cex_compile for structural validation
4. Retrieved by cex_retriever for context injection
5. Evolved by cex_evolve when quality regresses below target

## Metadata

```yaml
id: bld_tools_instruction
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-instruction.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_action_prompt]] | sibling | 0.69 |
| [[bld_tools_prompt_version]] | sibling | 0.66 |
| [[bld_tools_retriever_config]] | sibling | 0.65 |
| [[bld_tools_constraint_spec]] | sibling | 0.65 |
| [[bld_tools_memory_scope]] | sibling | 0.65 |
