---
id: bld_schema_landing_page
kind: schema
pillar: P06
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Esquema Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [construção de landing page, esquema landing page, landing_page, builder, examples, saída da landing page, open graph, integração do pipeline, artefatos relacionados, landing page]
density_score: 0.90
llm_function: CONSTRAIN
related:
  - bld_schema_tagline
  - bld_schema_model_registry
  - bld_config_landing_page
  - bld_schema_experiment_tracker
---
# Esquema: Saída da Landing Page

```yaml
# Required frontmatter
id: string               # unique landing page artifact id
kind: landing_page
pillar: P05
title: string            # page title (also <title> tag)
version: string
created: date
author: string
quality: null            # never self-score
tags: [landing-page, ...]
stack: enum[html-tailwind, react, nextjs, astro]
sections_count: integer  # number of sections
responsive: true
dark_mode: true
a11y: AA

# Body: the actual code
# Single HTML file OR component file(s)

# Metadata block (in frontmatter or separate)
seo:
  title: string
  description: string    # max 160 chars
  og_image: string       # Open Graph image URL
  canonical: string
  json_ld_type: enum[Organization, Product, SoftwareApplication, Course]

design_tokens:
  colors: {primary, secondary, accent, bg, text, muted}
  fonts: {heading, body, mono}
  radius: string
  shadow: string

sections:
  - id: string
    type: enum[hero, problem, solution, features, social-proof, how-it-works, pricing, testimonials, faq, cta, footer, meta]
    has_cta: boolean
    responsive: boolean
```

## Integração do Pipeline

1. Criado via pipeline 8F, de F1-Focus a F8-Furnish
2. Pontuado pelo cex_score em três camadas estruturais
3. Compilado pelo cex_compile para validação estrutural
4. Recuperado pelo cex_retriever para injeção de contexto
5. Evoluído pelo cex_evolve quando a qualidade regride abaixo da meta

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `schema` |
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
| n00_landing_page_manifest | upstream | 0.44 |
| [[bld_schema_tagline]] | sibling | 0.43 |
| bld_schema_model_registry | sibling | 0.41 |
| [[bld_config_landing_page]] | related | 0.40 |
| bld_schema_experiment_tracker | sibling | 0.39 |
