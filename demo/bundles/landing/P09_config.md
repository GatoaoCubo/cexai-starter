---
id: bld_config_landing_page
kind: config
pillar: P06
builder: landing-page-builder
version: 1.0.0
effort: high
max_turns: 30
disallowed_tools: []
permission_scope: nucleus
quality: null
title: "Configuração Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [construção de landing page, config landing page, landing_page, builder, examples, landing page builder, jetbrains mono, integração do pipeline, artefatos relacionados, landing page]
density_score: 0.90
llm_function: CONSTRAIN
related:
  - bld_schema_landing_page
  - bld_tools_landing_page
  - bld_memory_landing_page
---
# Configuração: Landing Page Builder

output_format: html
quality_floor: 8.5

defaults:
  stack: html-tailwind    # html-tailwind | react | nextjs | astro
  sections: 12
  mobile_first: true
  dark_mode: true
  tailwind_version: "3.4"
  font_provider: google-fonts
  image_placeholders: picsum
  analytics: gtm
  a11y_level: AA          # WCAG AA minimum

brand_injection:
  required: false
  fields: [BRAND_NAME, BRAND_COLORS, BRAND_FONTS, BRAND_TONE, BRAND_TAGLINE]
  fallback: generate_defaults

design_tokens:
  colors:
    primary: "#2563eb"    # blue-600
    secondary: "#7c3aed"  # violet-600
    accent: "#f59e0b"     # amber-500
    bg: "#ffffff"
    text: "#111827"       # gray-900
    muted: "#6b7280"      # gray-500
  fonts:
    heading: "Inter"
    body: "Inter"
    mono: "JetBrains Mono"
  radius: "0.5rem"
  shadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)"

## Integração do Pipeline

1. Criado via pipeline 8F, de F1-Focus a F8-Furnish
2. Pontuado pelo cex_score em três camadas estruturais
3. Compilado pelo cex_compile para validação estrutural
4. Recuperado pelo cex_retriever para injeção de contexto
5. Evoluído pelo cex_evolve quando a qualidade regride abaixo da meta

## Metadados

```yaml
id: bld_config_landing_page
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-config-landing-page.md
```

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `config` |
| Pillar | P06 |
| Domain | construção de landing page |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_schema_landing_page]] | related | 0.51 |
| [[bld_tools_landing_page]] | upstream | 0.41 |
| [[bld_orchestration_landing_page]] | downstream | 0.38 |
| [[bld_memory_landing_page]] | downstream | 0.37 |
| tpl_validation_schema | related | 0.37 |
