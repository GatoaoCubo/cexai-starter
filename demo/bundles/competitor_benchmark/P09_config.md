---
kind: config
id: bld_config_competitive_matrix
pillar: P09
llm_function: CONSTRAIN
purpose: Nomenclatura, caminhos, limites para produção de competitive_matrix
quality: null
title: "Config Competitive Matrix"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, config]
tldr: "Restrições de produção para a matriz competitiva: nomenclatura (p01_cm_{{name}}.md), caminhos de saída (P01/), limite de tamanho 5120B. Documento competitivo."
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for competitive_matrix production, competitive_matrix construction, config competitive matrix, output paths, size limit, competitive doc, competitive_matrix, builder, config, naming convention]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_repo_map
  - bld_config_discovery_questions
  - bld_config_ab_test_config
  - bld_config_agents_md
---

## Convenção de Nomenclatura (artefatos de matriz competitiva)
Padrão: p01_cm_{{name}}.md (ex.: p01_cm_market_analysis.md) para saídas de matriz competitiva

## Caminhos
/artifacts/p01/cm/{{name}}.md

## Limites
max_bytes: 5120
max_turns: 3
effort_level: high

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Restrições Específicas do Domínio

| Restrição | Valor |
|-----------|-------|
| Limite | Documento competitivo |
| Dependências | knowledge_card, customer_segment |
| Função 8F primária | F4_reason |
| Tamanho máximo do artefato | 5120 bytes |

## Casos de Borda

| Cenário | Tratamento |
|----------|---------|
| Campo obrigatório do frontmatter ausente | Falha no gate H01; retorna para F6 |
| Colisão de ID com artefato existente | Adiciona sufixo de versão (_v2) |
| Corpo excede 5120 bytes | Corta seções de prosa; preserva tabelas |
| Dependência knowledge_card não encontrada | Avisa; prossegue com padrões |

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domínio | construção de matriz competitiva |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compilador | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_config_api_reference | sibling | 0.53 |
| bld_config_repo_map | sibling | 0.53 |
| bld_config_discovery_questions | sibling | 0.51 |
| bld_config_ab_test_config | sibling | 0.50 |
| bld_config_agents_md | sibling | 0.50 |
