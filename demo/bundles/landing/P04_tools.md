---
id: bld_tools_landing_page
kind: tools
pillar: P04
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Ferramentas Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [construção de landing page, tools landing page, landing_page, builder, examples, brand_config_reader, cex_query.py, cex_retriever.py, browser_playwright, browser_design_extractor]
density_score: 0.90
llm_function: CALL
related:
  - bld_memory_landing_page
  - bld_schema_landing_page
  - bld_architecture_landing_page
---
# Ferramentas: Landing Page Builder

## Ferramentas Obrigatórias
1. `brand_config_reader`: lê os design tokens de .cex/brand/brand_config.yaml
2. `cex_query.py`: encontra a saída do tagline-builder, dados de preço, artefatos de marca
3. `cex_retriever.py`: busca templates de página e padrões de design existentes

## Ferramentas de Construção (disponíveis na stack)
1. `browser_playwright`: pré-visualiza a página gerada, tira screenshots, testa responsividade
2. `browser_design_extractor`: extrai design tokens de URLs de referência
3. `computer_use`: validação visual da página renderizada (opcional)

## Ferramentas de Referência
1. `browser_web_scraping`: analisa landing pages de concorrentes em busca de inspiração
2. `browser_awesome_list`: encontra recursos de design, sets de ícones, combinações de fontes

## Sem Dependências de Build para Saída em HTML
A saída padrão HTML+Tailwind CDN não exige NENHUMA ferramenta de build. O usuário salva
o arquivo e faz o deploy. Saídas em React/Next.js exigem o setup de projeto que o usuário
já tiver.

## Permissões de Ferramentas
1. LEITURA: brand config, artefatos existentes, páginas de concorrentes, recursos de design
2. ESCRITA: somente arquivos de saída (HTML/JSX da landing page + YAML compilado)
3. EXECUÇÃO: ferramentas de preview (browser_playwright, browser_design_extractor)
4. NEGADO: sem escrita em banco de dados, sem deploy, sem mutação em APIs externas

## Metadados

```yaml
id: bld_tools_landing_page
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-landing-page.md
```

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `tools` |
| Pillar | P04 |
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
| [[bld_orchestration_landing_page]] | downstream | 0.46 |
| [[bld_memory_landing_page]] | downstream | 0.42 |
| [[bld_schema_landing_page]] | downstream | 0.36 |
| [[bld_architecture_landing_page]] | downstream | 0.36 |
