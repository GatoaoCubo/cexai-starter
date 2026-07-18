---
id: bld_output_template_landing_page
kind: output_template
pillar: P05
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Modelo de Saída Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
keywords: [construção de landing page, output template landing page, landing_page, builder, examples, instruções de deploy, netlify, vercel, output template, landing page, design tokens]
density_score: 0.90
llm_function: PRODUCE
related:
  - bld_tools_landing_page
  - bld_schema_landing_page
  - bld_memory_landing_page
  - bld_architecture_landing_page
---
# Modelo de Saída: Landing Page

```markdown
---
id: landing_page_{{BRAND_SLUG}}
kind: landing_page
pillar: P05
title: "{{PAGE_TITLE}}"
version: 1.0.0
created: {{DATE}}
author: landing-page-builder
quality: null
tags: [landing-page, {{BRAND_SLUG}}, {{STACK}}, responsive, dark-mode]
stack: {{STACK}}
sections_count: {{SECTIONS_COUNT}}
responsive: true
dark_mode: true
a11y: AA
seo:
  title: "{{SEO_TITLE}}"
  description: "{{SEO_DESCRIPTION}}"
  og_image: "{{OG_IMAGE_URL}}"
---

# Landing Page: {{BRAND_NAME}}

## Design Tokens
| Token | Valor |
|-------|-------|
| Cor Primária | {{COLOR_PRIMARY}} |
| Cor Secundária | {{COLOR_SECONDARY}} |
| Fonte de Título | {{FONT_HEADING}} |
| Fonte de Corpo | {{FONT_BODY}} |

## Seções
{{SECTIONS_CHECKLIST}}

## Código

\`\`\`html
{{FULL_HTML_CODE}}
\`\`\`

## Instruções de Deploy
1. Salve como `index.html`
2. Substitua as imagens placeholder por assets reais
3. Substitua as variáveis {{BRAND_*}} pelos valores reais da marca
4. Faça deploy em: Vercel (`vercel deploy`) / Netlify (`netlify deploy`) / GitHub Pages
5. Teste no mobile (375px) e no desktop (1440px)
```

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `output_template` |
| Pillar | P05 |
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
| [[bld_tools_landing_page]] | upstream | 0.51 |
| [[bld_schema_landing_page]] | downstream | 0.50 |
| [[bld_memory_landing_page]] | downstream | 0.49 |
| [[bld_orchestration_landing_page]] | downstream | 0.48 |
| [[bld_architecture_landing_page]] | downstream | 0.45 |
