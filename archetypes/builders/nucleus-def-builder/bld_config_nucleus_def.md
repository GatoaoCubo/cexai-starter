---
kind: config
id: bld_config_nucleus_def
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for nucleus_def production
quality: null
title: "Config Nucleus Def"
version: "1.0.0"
author: n05_wave8
tags: [nucleus_def, builder, config]
tldr: "Naming, paths, limits for nucleus_def production"
domain: "nucleus_def construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for nucleus_def production, nucleus_def construction, config nucleus def, nucleus_def, builder, config, "nucleus_def_{{nucleus_id_lower}}.md", nucleus_def_n01.md, nucleus_def_n05.md, nucleus_def_n07.md]
density_score: 0.85
related:
  - nucleus_def_n03.md
  - nucleus_def_n01.md
  - nucleus_def_n04.md
  - bld_knowledge_card_nucleus_def
  - nucleus_def_n05.md
---
## Naming Convention
Pattern: `nucleus_def_`{{nucleus_id_lower}}`.md`
Examples: `nucleus_def_n01.md`, `nucleus_def_n05.md`, `nucleus_def_n07.md`
Regex: `^nucleus_def_n0[0-7]\.md$`

## Paths
Artifacts stored in: `N0{X}_*/P02_model/nucleus_def_`{{nucleus_id_lower}}`.md`
Builder ISOs: `archetypes/builders/nucleus-def-builder/`
Knowledge card: `P01_knowledge/library/kind/kc_nucleus_def.md`

## Limits
max_bytes: 5120
max_turns: 5
effort_level: 3

## Instance Set
| Artifact | Nucleus | Path |
|----------|---------|------|
| nucleus_def_n00.md | N00 Genesis | N00_genesis/P02_model/ |
| nucleus_def_n01.md | N01 Intelligence | N01_intelligence/P02_model/ |
| nucleus_def_n02.md | N02 Marketing | N02_marketing/P02_model/ |
| nucleus_def_n03.md | N03 Builder | N03_engineering/P02_model/ |
| nucleus_def_n04.md | N04 Knowledge | N04_knowledge/P02_model/ |
| nucleus_def_n05.md | N05 Operations | N05_operations/P02_model/ |
| nucleus_def_n06.md | N06 Commercial | N06_commercial/P02_model/ |
| nucleus_def_n07.md | N07 Orchestrator | N07_admin/P02_model/ |

## Hooks
pre_build: validate nucleus_id is in [N00..N07]
post_build: python _tools/cex_compile.py {path}
on_error: report missing source file (nucleus_models.yaml, agent_card, rule file)
on_quality_fail: re-verify pillars_owned against actual artifact production

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| nucleus_def_n03.md | upstream | 0.25 |
| nucleus_def_n01.md | upstream | 0.24 |
| nucleus_def_n04.md | upstream | 0.23 |
| [[bld_knowledge_card_nucleus_def]] | upstream | 0.23 |
| nucleus_def_n05.md | upstream | 0.22 |
