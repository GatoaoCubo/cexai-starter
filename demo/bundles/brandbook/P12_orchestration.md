---
id: bld_orchestration_brandbook
kind: workflow
pillar: P12
builder: brandbook-builder
version: 1.0.0
quality: null
title: Orchestration -- brandbook
author: n06_commercial
tags: [workflow, brandbook, P12]
llm_function: COLLABORATE
created: 2026-06-22
updated: 2026-06-22
related:
  - kc_brandbook
  - p12_ct_brand_discovery
  - p02_ra_visual_packager
  - bld_architecture_brandbook
  - brandbook-builder
  - bld_prompt_brandbook
  - bld_knowledge_brandbook
  - p01_kc_workflow_orchestration
  - p12_dr_content_factory
  - bld_tools_brandbook
---

## Orquestração: brandbook

### Build Solo (gerador único)
```bash
python _tools/cex_8f_runner.py "build brandbook for {brand_name}" \
  --kind brandbook --nucleus n06 --execute
```

### Build da Crew (sequencial de 3 papéis)
```bash
python _tools/cex_crew.py run brand_discovery \
  --charter N06_commercial/P12_orchestration/crews/team_charter_brand_default.md \
  --execute
```

### Posicionamento de Wave no Grid
brandbook é construído na Wave 2 (depois da crew de brand discovery, antes da fábrica de conteúdo):
```
Wave 1: N01 brand research (competitive intelligence, positioning)
Wave 2: N06 brand_discovery crew -> brandbook-builder
Wave 3: N02 content factory (uses brandbook as context)
Wave 4: N03 landing page / design_system (uses brandbook tokens)
```

### Consumidores Downstream
| Artefato | Como usa o brandbook |
|----------|------------------------|
| landing_page (P05) | Injeta paleta + tipografia + copy do headline |
| design_system (P06) | Consome paleta + tipografia para os tokens |
| white_label_config (P09) | Consome o hex da paleta -> formato de 24 tokens HSL |
| content calendar (N02) | Injeta a voz da persona de marca + framework de mensagem |
| ad_copy (N02) | Injeta exemplos de copy como sementes de copy |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_brandbook]] | upstream | 0.50 |
| [[p12_ct_brand_discovery]] | related | 0.40 |
| [[p02_ra_visual_packager]] | upstream | 0.37 |
| [[bld_architecture_brandbook]] | upstream | 0.37 |
| [[brandbook-builder]] | upstream | 0.37 |
| [[bld_prompt_brandbook]] | upstream | 0.33 |
| [[bld_knowledge_brandbook]] | upstream | 0.29 |
| [[p01_kc_workflow_orchestration]] | upstream | 0.29 |
| [[p12_dr_content_factory]] | related | 0.27 |
| [[bld_tools_brandbook]] | upstream | 0.25 |
