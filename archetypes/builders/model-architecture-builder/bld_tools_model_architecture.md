---
kind: tools
id: bld_tools_model_architecture
pillar: P04
llm_function: CALL
quality: null
title: "Tools Model Architecture"
version: "1.0.0"
author: n05_builder
tags: [model_architecture, tools, P04, builder]
tldr: "Tools for model-architecture-builder: retriever, doctor, compiler, validator."
domain: "model_architecture construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F5_call"
keywords: [model_architecture construction, tools model architecture, tools for model-architecture-builder, model_architecture, tools, builder, python _tools/cex_retriever.py model_architecture, python _tools/cex_doctor.py, "python _tools/cex_compile.py {path}", "python _tools/cex_hooks.py validate {path}"]
density_score: 0.88
related:
  - bld_tools_training_method
  - bld_architecture_model_architecture
  - bld_tools_context_map
  - bld_tools_event_schema
---
# Tools: model-architecture-builder

## Build-Time Tools
| Tool | Command | When to Use |
|------|---------|------------|
| Retriever | `python _tools/cex_retriever.py model_architecture` | Find similar architecture specs |
| Doctor | `python _tools/cex_doctor.py` | Verify builder completeness (13 ISOs) |
| Compiler | `python _tools/cex_compile.py {path}` | Compile artifact after save |
| Hooks | `python _tools/cex_hooks.py validate {path}` | Validate frontmatter |
| Score | `python _tools/cex_score.py --apply {path}` | Request quality score |

## Validation Tools
| Tool | Command | Purpose |
|------|---------|---------|
| Schema check | `python _tools/cex_hooks.py pre-save {path}` | Validate required fields |
| Size check | `wc -c {path}` | Verify <= 4096 bytes body |
| ASCII check | `python _tools/cex_sanitize.py --check {path}` | Verify ASCII in code blocks |

## Integration Points
| System | How | Purpose |
|--------|-----|---------|
| finetune_config | model_architecture -> finetune_config | Architecture defines model; finetune spec trains it |
| model_card | model_architecture -> model_card | Card documents the trained architecture |
| training_method | model_architecture -> training_method | Architecture constrains training approach |
| model_provider | model_architecture -> model_provider | Architecture determines serving requirements |
| benchmark | model_architecture -> benchmark | Architecture compared via benchmarks |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_training_method]] | sibling | 0.43 |
| [[bld_architecture_model_architecture]] | downstream | 0.33 |
| [[bld_tools_context_map]] | sibling | 0.33 |
| [[bld_tools_event_schema]] | sibling | 0.32 |
