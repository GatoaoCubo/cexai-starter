---
id: bld_architecture_brandbook
kind: diagram
pillar: P08
builder: brandbook-builder
version: 1.0.0
quality: null
title: Architecture -- brandbook
author: n06_commercial
tags: [diagram, brandbook, P08]
llm_function: CONSTRAIN
created: 2026-06-22
updated: 2026-06-22
related:
  - kc_brandbook
  - p02_ra_visual_packager
  - brandbook-builder
  - bld_orchestration_brandbook
  - p12_ct_brand_discovery
  - bld_prompt_brandbook
  - bld_knowledge_brandbook
  - bld_memory_brandbook
  - bld_tools_brandbook
  - spec_dual_output_contract
---

## Fluxo de Dados do Brandbook

```
INPUTS                          GENERATOR                       OUTPUTS
------                          ---------                       -------
brand_name (required)
brand_essence (optional)        brandbook.build(inputs)
brand_materials (file/url/text) --->                            8 output_sections
  |                                                             (frozen shape)
  v (Cell A pre-processes)
brand_materials_text            F1 CONSTRAIN                   StructuredOutput
brand_materials_palette    ---> F3 INJECT (palette, text)      + artifact JSON
brand_materials_data_uri        F6 PRODUCE (8 sections)        + notes
                                F7 GOVERN (gate + score)
                                      |
                                      v
                                cex_dual_output.to_dual_output
                                      |
                          +-----------+-----------+
                          |                       |
                     MACHINE face            HUMAN face
                   .md + YAML frontmatter   HTML audiovisual
                   (id/brand/sections)      (sections + media slots)
                   persisted tenant-scoped  logo + palette + cover
```

## Integração da Crew de Marca

```
brand_discovery crew (sequential, 3 roles)
  |
  +-- Brand Strategist  --> positioning_brief (knowledge_card)
        |
        +-- Persona Architect --> personality + tagline artifacts
              |
              +-- Visual Packager --> design_system + white_label_config
                    |
                    +-- brandbook-builder consumes all 3 artifacts
                          |
                          v
                    p05_bb_{brand}.md (final brandbook)
```

## Mapa de Composição
| Kind composto | Onde é usado | Builder |
|-----------------|----------------|---------|
| personality (P02) | Seção 4 Persona | personality-builder |
| design_system (P06) | Seções 2+3 | design-system-builder |
| white_label_config (P09) | Seções 2+3 (24 tokens HSL) | white-label-config-builder |
| tagline (P03) | Seção 1 Identidade | tagline-builder |

### Nota de Portabilidade (bundle exportado)
Os dois diagramas acima mostram como o CEXAI **interno** constrói e audita a
capacidade brandbook -- incluindo a crew sequencial de 3 papéis
(`brand_discovery`) e o pipeline F1-F7 completo. O agente standalone deste
bundle roda apenas a etapa final: recebe `brand_name` + `brand_essence` +
`brand_materials` diretamente do usuário, em uma única conversa, e produz as
mesmas 8 seções -- sem rodar a crew upstream nem o `cex_dual_output` de
duas faces. O "HUMAN face" (HTML audiovisual) e o "MACHINE face" (.md +
frontmatter YAML) descritos no primeiro diagrama existem no CEXAI interno;
aqui, a saída é só o documento Markdown das 8 seções, pronto para copiar.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_brandbook]] | upstream | 0.43 |
| [[p02_ra_visual_packager]] | upstream | 0.36 |
| [[brandbook-builder]] | upstream | 0.34 |
| [[bld_orchestration_brandbook]] | downstream | 0.33 |
| [[p12_ct_brand_discovery]] | downstream | 0.32 |
| [[bld_prompt_brandbook]] | upstream | 0.26 |
| [[bld_knowledge_brandbook]] | upstream | 0.24 |
| [[bld_memory_brandbook]] | downstream | 0.24 |
| [[bld_tools_brandbook]] | upstream | 0.24 |
| [[spec_dual_output_contract]] | upstream | 0.21 |
