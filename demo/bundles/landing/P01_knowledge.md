---
id: bld_knowledge_card_landing_page
kind: knowledge_card
pillar: P01
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Cartão de Conhecimento Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F3_inject"
keywords: [construção de landing page, cartão de conhecimento landing page, landing_page, builder, examples, knowledge card, landing page, psicologia das seções, papel na conversão, hospedagem estática]
density_score: 0.90
llm_function: INJECT
related:
  - kc_landing_page
  - landing-page-builder
  - bld_architecture_landing_page
  - bld_tools_landing_page
---
# Cartão de Conhecimento: Landing Page

## O que é uma Landing Page?
Uma landing page é uma página web autônoma, projetada para uma única meta de conversão.
Diferente de um site completo com navegação, a landing page foca o visitante em UMA ação:
cadastrar-se, comprar, baixar ou agendar.

## Psicologia das Seções
| Seção | Propósito | Papel na Conversão |
|---------|---------|-----------------|
| Hero | Primeira impressão, proposta de valor | Gancho (decisão em 3 segundos) |
| Problem | Empatia, "eles me entendem" | Amplificação da dor |
| Solution | Alívio, "isso resolve" | Promessa |
| Features | Justificativa racional | Reforço lógico |
| Social Proof | Confiança, "outras pessoas confiam nisso" | Redução de risco |
| How It Works | Simplicidade, "é fácil" | Tratamento de objeções |
| Pricing | Decisão, "quanto custa" | Enquadramento de valor |
| Testimonials | Histórias, "gente como eu" | Validação social |
| FAQ | Objeções, "mas e quanto a..." | Eliminação final de objeções |
| CTA | Urgência, "faça agora" | Gatilho de conversão |

## Boas Práticas de Conversão
- Acima da dobra: headline + subheadline + CTA visíveis sem precisar rolar a página
- Um CTA por seção (repetido, porém consistente)
- Leitura em padrão F para desktop, coluna única para mobile
- Hierarquia visual: texto maior = mensagem mais importante
- Espaço em branco > poluição visual (respiro visual aumenta a compreensão)
- Velocidade de carregamento: cada 100ms de atraso = -7% de conversão (dado do Google)

## Comparativo de Stacks
| Stack | Etapa de Build | Melhor Para | Deploy |
|-------|-----------|----------|--------|
| HTML + Tailwind CDN | Nenhuma | Páginas rápidas, não-devs | Qualquer hospedagem estática |
| React + Tailwind | npm build | Apps React existentes | Vercel, Netlify |
| Next.js | next build | Crítico para SEO, precisa de SSR | Vercel |
| Astro | astro build | Multi-página, rico em conteúdo | Qualquer hospedagem estática |

## Concorrentes que Substituímos
| Ferramenta | O que fazem | O que fazemos diferente |
|------|-------------|----------------------|
| Lovable | IA constrói web apps a partir de prompts | Entregamos o CÓDIGO, sem prender você a uma plataforma |
| Bolt.new | IA gera apps full-stack | Focamos em páginas otimizadas para conversão |
| v0.dev | IA gera componentes de UI | Construímos páginas COMPLETAS, não componentes |
| Framer | Construtor visual de páginas | Produzimos código que você possui e modifica |
| Webflow | Construtor de páginas no-code | Produzimos HTML/React portável, sem vendor lock-in |

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[kc_landing_page]] | sibling | 0.59 |
| [[landing-page-builder]] | downstream | 0.46 |
| [[bld_architecture_landing_page]] | downstream | 0.39 |
| [[bld_tools_landing_page]] | downstream | 0.39 |
| [[bld_orchestration_landing_page]] | downstream | 0.38 |
