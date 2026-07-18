---
id: bld_instruction_landing_page
kind: instruction
pillar: P03
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Instrução Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
keywords: [construção de landing page, instrução landing page, landing_page, builder, examples, pipeline de construção de landing page, usar tailwind, open graph, opções de stack, app router]
density_score: 0.90
llm_function: REASON
related:
  - landing-page-builder
  - kc_landing_page
  - bld_architecture_landing_page
  - bld_schema_landing_page
---
# Instrução: Pipeline de Construção de Landing Page

## Etapas
1. **BRIEF** -- Reúna: brand_config OU input do usuário (produto, público, objetivo, tom de voz, preferência de stack)
2. **STRUCTURE** -- Escolha a ordem das seções com base no objetivo:
   - Produto SaaS: HERO > FEATURES > SOCIAL-PROOF > PRICING > FAQ > CTA
   - Serviço/Agência: HERO > PROBLEM > SOLUTION > HOW-IT-WORKS > TESTIMONIALS > CTA
   - Curso/Infoproduto: HERO > PROBLEM > TRANSFORMATION > MODULES > PRICING > FAQ > CTA > GUARANTEE
   - Portfólio: HERO > WORK > ABOUT > TESTIMONIALS > CONTACT
3. **DESIGN TOKENS** -- Extraia do brand_config ou defina:
   - Cores: primary, secondary, accent, bg, text, muted
   - Fontes: heading (display), body (sans), mono
   - Espaçamento: padding das seções, gaps entre componentes
   - Border radius, profundidade de shadow
4. **BUILD** -- Gere cada seção como um bloco autocontido:
   - Cada seção tem: id, aria-label, classes responsivas, CTA ou interação
   - Use classes utilitárias do Tailwind (CSS customizado somente quando inevitável)
   - Componentes shadcn/ui para elementos interativos (accordion, dialog, tabs)
5. **ASSEMBLE** -- Combine em um único arquivo com:
   - DOCTYPE, html lang, head (meta, fontes, Tailwind CDN), body
   - Smooth scroll, scroll-margin para nav ancorada
   - JS: toggle do menu mobile, accordion do FAQ, animações de scroll (IntersectionObserver)
6. **OPTIMIZE** -- Adicione:
   - Meta tags de Open Graph (title, description, image, url)
   - Dados estruturados JSON-LD (Organization ou Product)
   - Atributos de dados GTM/GA4 nos CTAs
   - Lazy loading nas imagens abaixo da dobra
   - Stylesheet básico de impressão
7. **VALIDATE** -- Verifique:
   - Todas as 12 seções presentes (ou omissão justificada)
   - Responsivo no mobile (sem rolagem horizontal)
   - Todos os CTAs têm href ou onclick
   - Todas as imagens têm texto alternativo (alt)
   - Contraste de cor passa no WCAG AA

## Opções de Stack
| Stack | Quando | Saída |
|-------|------|--------|
| HTML + Tailwind CDN | Padrão, zero build | Um único arquivo .html |
| React + Tailwind | Usuário tem projeto React | Componente .tsx |
| Next.js App Router | Usuário tem Next.js | page.tsx + layout.tsx |
| Astro | Usuário quer saída estática | Página .astro |

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[landing-page-builder]] | downstream | 0.49 |
| [[kc_landing_page]] | upstream | 0.45 |
| [[bld_architecture_landing_page]] | downstream | 0.42 |
| [[bld_schema_landing_page]] | downstream | 0.36 |
