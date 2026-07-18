---
id: bld_architecture_landing_page
kind: architecture
pillar: P08
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Arquitetura Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [construção de landing page, arquitetura landing page, landing_page, builder, examples, arquitetura de stack, modelo de componente de seção, landing page builder, google fonts]
density_score: 0.90
llm_function: CONSTRAIN
related:
  - kc_landing_page
  - bld_tools_landing_page
  - landing-page-builder
---
# Arquitetura: Landing Page Builder

## Pipeline
```
BRIEF → STRUCTURE → DESIGN_TOKENS → BUILD(12 sections) → ASSEMBLE → OPTIMIZE(SEO+A11y+Perf) → VALIDATE
```

## Modelo de Componente de Seção
Cada seção é um bloco autocontido:
```
<section id="{name}" aria-label="{label}" class="py-16 md:py-24 {bg}">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    {content}
  </div>
</section>
```

## Arquitetura de Stack
```
HTML + Tailwind CDN (default)
├── index.html (single file, everything inline)
├── Tailwind via CDN <script> (no build step)
├── Google Fonts via <link>
├── JS: inline <script> at bottom (menu, accordion, scroll)
└── Deploy: any static host (Vercel, Netlify, S3, GitHub Pages)

React + Tailwind (optional)
├── page.tsx (component)
├── components/ (Section components)
├── lib/design-tokens.ts
└── Deploy: Vercel, any React host

Next.js App Router (optional)
├── app/page.tsx
├── app/layout.tsx (fonts, metadata)
├── components/sections/
└── Deploy: Vercel
```

## Dependências
1. brand_config.yaml (opcional -- na ausência, os design tokens usam os padrões)
2. saída do tagline-builder (opcional -- headline do hero)
3. Sem dependências de runtime para a saída HTML (zero JS, exceto interações)

## Pontos de Integração
1. tagline-builder → headline e sub-headline do hero
2. social-publisher-builder → meta tags de Open Graph para compartilhamento social
3. content-monetization-builder → planos da seção de pricing
4. N02 Marketing → landing pages específicas de campanha
5. N05 Operations → pipeline de deploy (Vercel/Netlify/S3)

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `architecture` |
| Pillar | P08 |
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
| [[bld_orchestration_landing_page]] | downstream | 0.45 |
| [[kc_landing_page]] | upstream | 0.38 |
| [[bld_tools_landing_page]] | upstream | 0.38 |
| [[landing-page-builder]] | upstream | 0.37 |
