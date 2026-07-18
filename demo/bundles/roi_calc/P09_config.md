---
kind: config
id: bld_config_roi_calculator
pillar: P09
llm_function: CONSTRAIN
purpose: Nomenclatura, caminhos e limites para produção de roi_calculator
quality: null
title: "Configuração -- ROI Calculator"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [roi_calculator, builder, config]
tldr: "Restrições de produção para o roi calculator: nomenclatura (p11_roi_{{name}}.yaml), caminhos de saída (P11/), limite de tamanho 4096B. ROI calc."
domain: "construção de roi_calculator"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limites para produção de roi_calculator, construção de roi_calculator, configuração roi calculator, caminhos de saída, limite de tamanho, roi calc, roi_calculator, builder, config, "p11_roi_{{name}}.yaml"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_safety_policy
  - bld_config_api_reference
  - bld_config_content_filter
  - bld_config_collaboration_pattern
---

## Convenção de Nomenclatura
Padrão: `p11_roi_{{name}}.yaml`
Exemplos: `p11_roi_projectA.yaml`, `p11_roi_q4_2023.yaml`

## Caminhos
Artefatos: `/artifacts/roi/p11/{{name}}/output.yaml`
Logs: `/artifacts/roi/p11/{{name}}/logs/`

## Limites
max_bytes: 4096
max_turns: 10
effort_level: medium

## Ganchos
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Restrições Específicas do Domínio

| Restrição | Valor |
|-----------|-------|
| Limite (boundary) | ROI calc |
| Dependências | customer_segment, eval_metric |
| Função 8F primária | F6_produce |
| Tamanho máximo do artefato | 4096 bytes |

## Casos-Limite

| Cenário | Tratamento |
|----------|---------|
| Campo obrigatório de frontmatter ausente | Falha no gate H01; retorna para F6 |
| Colisão de ID com artefato existente | Acrescenta sufixo de versão (_v2) |
| Corpo excede 4096 bytes | Reduz seções de prosa; preserva as tabelas |
| Dependência customer_segment não encontrada | Avisa; prossegue com os padrões |

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domínio | construção de roi calculator |
| Pipeline | 8F (F1-F8) |
| Avaliador (Scorer) | cex_score.py |
| Compilador | cex_compile.py |
| Recuperador (Retriever) | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_ab_test_config | sibling | 0.51 |
| bld_config_safety_policy | sibling | 0.48 |
| bld_config_api_reference | sibling | 0.48 |
| [[bld_config_content_filter]] | sibling | 0.47 |
| bld_config_collaboration_pattern | sibling | 0.47 |
