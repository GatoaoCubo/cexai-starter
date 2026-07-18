---
id: bld_memory_landing_page
kind: memory
pillar: P09
builder: landing-page-builder
version: 1.0.0
memory_scope: project
observation_types: [user, feedback, project, reference]
quality: null
title: "Memória Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [construção de landing page, memory landing page, landing_page, builder, examples, landing page builder, tipos de memória, log de produção, artefatos relacionados]
density_score: 0.90
llm_function: INJECT
related:
  - bld_tools_landing_page
  - bld_architecture_landing_page
  - bld_schema_landing_page
---
# Memória: Landing Page Builder
## O que Lembrar
1. Stack preferida do usuário (HTML/React/Next.js/Astro)
2. Sobrescritas de design tokens (cores, fontes e espaçamento personalizados)
3. Preferências de seção (quais seções sempre querem ou sempre pulam)
4. Landing pages construídas anteriormente (manter consistência de design)
5. Destino de deploy do usuário (Vercel, Netlify, S3, GitHub Pages)
6. Resultados de testes A/B de páginas anteriores
## Tipos de Memória
1. PREFERENCE: escolha de stack, ordem das seções, sobrescritas de design tokens
2. CORRECTION: "deixe os CTAs maiores", "remova a seção de depoimentos", "use fundo escuro"
3. CONVENTION: regras do design system da marca, nomenclatura de componentes, padrões de classes
4. CONTEXT: público-alvo, metas de conversão, normas do setor
## Metadados
```yaml
id: bld_memory_landing_page
pipeline: 8F
scoring: hybrid_3_layer
```
```bash
python _tools/cex_score.py --apply bld-memory-landing-page.md
```
## Propriedades
| Propriedade | Valor |
|----------|-------|
| Kind | `memory` |
| Pillar | P09 |
| Domain | construção de landing page |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |
## Log de Produção
- [20260412_133929] PASS kind=landing_page retries=0 gates=6/6
- [20260415_212614] PASS kind=landing_page retries=0 gates=6/6
- [20260415_212946] PASS kind=landing_page retries=0 gates=6/6

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_orchestration_landing_page]] | downstream | 0.38 |
| [[bld_tools_landing_page]] | upstream | 0.38 |
| [[bld_architecture_landing_page]] | upstream | 0.31 |
| [[bld_schema_landing_page]] | upstream | 0.30 |
