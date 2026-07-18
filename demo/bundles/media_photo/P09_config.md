---
kind: config
id: bld_config_multimodal_prompt
pillar: P09
llm_function: CONSTRAIN
purpose: Nomenclatura, caminhos e limites para a produção de multimodal_prompt
quality: null
title: "Config Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, config]
tldr: "Restrições de produção para multimodal prompt: nomenclatura (p03_mmp_{{name}}.md), caminhos de saída (P03/), limite de tamanho 4096B. Multimodal prompt."
domain: "construção de multimodal_prompt"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limites para a produção de multimodal_prompt, construção de multimodal_prompt, config multimodal prompt, caminhos de saída, limite de tamanho, multimodal prompt, multimodal_prompt, builder, config, convenção de nomenclatura, padrão]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_prompt_technique
  - bld_config_api_reference
  - bld_config_prompt_optimizer
  - bld_config_planning_strategy
---

## Convenção de Nomenclatura
Padrão: p03_mmp_<project>_<module>.md
Exemplos: p03_mmp_cex_core.md, p03_mmp_ai_vision.md

## Caminhos
Artefatos: /mnt/data/cex/p03/mmp/<project>/artifacts
Logs: /var/log/cex/p03/mmp/<project>

## Limites
max_bytes: 4096
max_turns: 10
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Restrições Específicas do Domínio

| Restrição | Valor |
|-----------|-------|
| Fronteira | Multimodal prompt |
| Dependências | prompt_template |
| Função 8F primária | F6_produce |
| Tamanho máximo do artefato | 4096 bytes |

## Casos de Borda

| Cenário | Tratamento |
|----------|---------|
| Campo de frontmatter obrigatório ausente | Falha no gate H01; retorna ao F6 |
| Colisão de ID com artefato existente | Adiciona sufixo de versão (_v2) |
| Corpo excede 4096 bytes | Corta seções de prosa; preserva tabelas |
| Dependência prompt_template não encontrada | Avisa; prossegue com padrões |

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domínio | construção de multimodal prompt |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compilador | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_ab_test_config | sibling | 0.50 |
| bld_config_prompt_technique | sibling | 0.49 |
| bld_config_api_reference | sibling | 0.48 |
| bld_config_prompt_optimizer | sibling | 0.48 |
| bld_config_planning_strategy | sibling | 0.48 |
