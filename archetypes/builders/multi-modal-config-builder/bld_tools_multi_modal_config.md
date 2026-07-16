---
kind: tools
id: bld_tools_multi_modal_config
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for multi_modal_config production
quality: null
title: "Tools Multi Modal Config"
version: "1.0.0"
author: n03_builder
tags: [multi_modal_config, builder, examples]
tldr: "Golden and anti-examples for multi modal config construction, demonstrating ideal structure and common pitfalls."
domain: "multi modal config construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [multi modal config construction, tools multi modal config, multi_modal_config, builder, examples, production tools, data sources, tool permissions, pipeline integration, related artifacts]
density_score: 0.90
related:
  - bld_tools_context_window_config
  - bld_tools_prompt_cache
  - bld_tools_citation
  - bld_tools_retriever_config
  - bld_tools_path_config
---

# Tools: multi-modal-config-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| cex_compile.py | Compile .md to .yaml | Phase 3 | ACTIVE |
| cex_retriever.py | Search existing configs | Phase 1 | ACTIVE |
| cex_token_budget.py | Estimate token costs per modality | Phase 2 | ACTIVE |
## Data Sources
| Source | Path | Data |
|--------|------|------|
| CEX Schema | P04_tools/_schema.yaml | Config field definitions |
| Kind KC | P01_knowledge/library/kind/kc_multi_modal_config.md | Deep knowledge |
| Model configs | .cex/config/nucleus_models.yaml | Model capabilities |
## Tool Permissions
| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | — |

## Pipeline Integration

1. Created via 8F pipeline from F1-Focus through F8-Furnish
2. Scored by cex_score across three structural layers
3. Compiled by cex_compile for structural validation
4. Retrieved by cex_retriever for context injection
5. Evolved by cex_evolve when quality regresses below target

## Metadata

```yaml
id: bld_tools_multi_modal_config
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-multi-modal-config.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_context_window_config]] | sibling | 0.60 |
| [[bld_tools_prompt_cache]] | sibling | 0.54 |
| [[bld_tools_citation]] | sibling | 0.52 |
| [[bld_tools_retriever_config]] | sibling | 0.47 |
| [[bld_tools_path_config]] | sibling | 0.44 |
