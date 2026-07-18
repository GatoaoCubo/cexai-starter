---
id: bld_collaboration_landing_page
kind: collaboration
pillar: P12
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Colaboração Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [construção de landing page, collaboration landing page, landing_page, builder, examples, landing page builder, open graph, comportamento no crew, artefatos relacionados]
density_score: 0.90
llm_function: COLLABORATE
related:
  - bld_tools_landing_page
  - bld_architecture_landing_page
  - bld_memory_landing_page
---
# Colaboração: Landing Page Builder

## Upstream (recebe de)
1. brand_config.yaml → cores, fontes, tom de voz, URL do logo
2. tagline-builder → headline do hero, sub-headline, texto do CTA
3. content-monetization-builder → planos de preço, listas de funcionalidades
4. N01 Research → análise de páginas de concorrentes, posicionamento de mercado
5. N06 Commercial → estratégia de preços, metas de conversão

## Downstream (envia para)
1. N05 Operations → deploy (Vercel, Netlify, S3, GitHub Pages)
2. social-publisher-builder → previews de Open Graph para compartilhamento social
3. N02 Marketing → landing pages de campanha, variantes de teste A/B
4. N04 Knowledge → templates de página adicionados à biblioteca de conhecimento

## Comportamento no Crew
1. Em um crew, o landing-page-builder roda POR ÚLTIMO (precisa primeiro de tagline, pricing e brand tokens)
2. Consome as saídas do tagline-builder e do content-monetization-builder
3. Produz um artefato PRONTO PARA DEPLOY, não uma especificação de design
4. Se testes A/B forem solicitados, produz 2 variantes com diferenciais claros

## Metadados

```yaml
id: bld_collaboration_landing_page
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-collaboration-landing-page.md
```

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `collaboration` |
| Pillar | P12 |
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
| [[bld_tools_landing_page]] | upstream | 0.45 |
| [[bld_architecture_landing_page]] | upstream | 0.41 |
| [[bld_memory_landing_page]] | upstream | 0.41 |
| [[bld_orchestration_tagline]] | sibling | 0.39 |
