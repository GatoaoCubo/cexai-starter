---
kind: config
id: bld_config_knowledge_card
pillar: P09
llm_function: CONSTRAIN
purpose: Convenções de nomenclatura, caminhos de arquivo, limites de tamanho, restrições operacionais
pattern: o CONFIG restringe o SCHEMA, nunca o contradiz
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: fork
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config: Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos ideais e contraexemplos para a construção de knowledge cards, demonstrando estrutura ideal e erros comuns."
domain: "construção de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [convenções de nomenclatura, caminhos de arquivo, limites de tamanho, restrições operacionais, construção de knowledge_card, config knowledge card, knowledge_card, builder, examples, "p01_kc_{topic_slug}.md"]
density_score: 0.90
related:
  - bld_config_output_validator
---
# Config: Regras de Produção do knowledge_card
## Convenção de Nomenclatura
| Escopo | Convenção | Exemplo |
|-------|-----------|---------|
| Arquivos de artifact | `p01_kc_{topic_slug}.md` | `p01_kc_prompt_caching.md` |
| Diretório do builder | kebab-case | `knowledge-card-builder/` |
| Campos de frontmatter | snake_case | `density_score`, `when_to_use` |
| Slug de tópico | minúsculo, underscores | `rag_fundamentals`, `prompt_caching` |
Regra: o id DEVE ser igual ao nome do arquivo sem extensão (o validador confere isso no H02).
## Caminhos de Arquivo
- Saída: `cex/P01_knowledge/examples/p01_kc_{topic}.md`
- Compilado: `cex/P01_knowledge/compiled/p01_kc_{topic}.yaml`
## Limites de Tamanho (alinhados com o SCHEMA)
- Corpo: 200-5120 bytes (validador H08)
- Total (frontmatter + corpo): máximo ~6500 bytes
- Densidade: >= 0.80
- Bullet máximo: 80 caracteres (validador S10)
- Title: 5-100 caracteres (validador S03)
- tldr: <= 160 caracteres, sem autorreferência (S01, S02)
## Requisitos do Corpo
- >= 4 seções (validador S06)
- Cada seção com >= 3 linhas não vazias (validador S08)
- A maior seção >= 30% do corpo (validador S07)
- >= 1 tabela (S11), >= 1 bloco de código (S12), >= 1 URL (S13)
## Seleção do Tipo de KC
| Conteúdo | Tipo | Estrutura de Corpo |
|---------|------|---------------|
| Tecnologia externa (APIs, padrões) | domain_kc | Referência Rápida + Conceitos + Fases + Regras + Fluxo + Comparativo + Referências |
| Interno ao CEX (arquitetura) | meta_kc | Resumo + Especificações + Padrões + Antipadrões + Aplicação + Referências |
Padrão: domain_kc. Use meta_kc só para documentação do sistema CEX.
## Atualidade
- o campo updated deve refletir a última edição relevante
- o conhecimento degrada mais devagar que model_card (sem gate rígido de 90 dias)
- KCs desatualizados são identificados pelo ranking de atualidade do brain_query

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_output_validator]] | sibling | 0.35 |
| [[bld_orchestration_output_validator]] | downstream | 0.34 |
| p01_kc_knowledge_best_practices | upstream | 0.30 |
