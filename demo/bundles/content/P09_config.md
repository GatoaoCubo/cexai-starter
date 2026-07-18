---
kind: config
id: bld_config_knowledge_card
pillar: P09
llm_function: CONSTRAIN
purpose: "Convencoes de nomenclatura, caminhos de arquivo, limites de tamanho, restricoes operacionais"
pattern: "o CONFIG restringe o SCHEMA, nunca o contradiz"
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
title: "Configuracao: knowledge_card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos de construcao de knowledge_card, demonstrando estrutura ideal e armadilhas comuns."
domain: "construcao de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, knowledge card construction, config knowledge card, knowledge_card, builder, examples, "p01_kc_{topic_slug}.md"]
density_score: 0.90
related:
  - bld_config_output_validator
---
# Configuracao: Regras de Producao do knowledge_card
## Convencao de Nomenclatura
| Escopo | Convencao | Exemplo |
|-------|-----------|---------|
| Arquivos de artefato | `p01_kc_{topic_slug}.md` | `p01_kc_prompt_caching.md` |
| Diretorio do builder | kebab-case | `knowledge-card-builder/` |
| Campos de frontmatter | snake_case | `density_score`, `when_to_use` |
| Slug do topico | minusculo, com underscores | `rag_fundamentals`, `prompt_caching` |
Regra: o id DEVE ser igual ao stem do nome do arquivo (o validador confere isso no H02).
## Caminhos de Arquivo
- Saida: `cex/P01_knowledge/examples/p01_kc_{topic}.md`
- Compilado: `cex/P01_knowledge/compiled/p01_kc_{topic}.yaml`
## Limites de Tamanho (alinhados com o SCHEMA)
- Corpo: 200-5120 bytes (validador H08)
- Total (frontmatter + corpo): maximo ~6500 bytes
- Densidade: >= 0.80
- Bullet maximo: 80 caracteres (validador S10)
- Title: 5-100 caracteres (validador S03)
- tldr: <= 160 caracteres, sem auto-referencia (S01, S02)
## Requisitos de Corpo
- >= 4 secoes (validador S06)
- Cada secao com >= 3 linhas nao vazias (validador S08)
- A maior secao com >= 30% do corpo (validador S07)
- >= 1 tabela (S11), >= 1 bloco de codigo (S12), >= 1 URL (S13)
## Selecao do Tipo de KC
| Conteudo | Tipo | Estrutura de Corpo |
|---------|------|---------------|
| Tecnologia externa (APIs, padroes) | domain_kc | Referencia Rapida + Conceitos + Fases + Regras + Fluxo + Comparativo + Referencias |
| Interno ao CEX (arquitetura) | meta_kc | Resumo + Especificacao + Padroes + Anti-Padroes + Aplicacao + Referencias |
Padrao: domain_kc. Use meta_kc somente para documentacao interna do sistema CEX.
## Atualidade (Freshness)
- o campo updated deve refletir a ultima edicao relevante
- o conhecimento se degrada mais devagar que model_cards (sem portao duro de 90 dias)
- KCs desatualizados sao identificados pelo ranking de atualidade do brain_query

## Related Artifacts
| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[bld_config_output_validator]] | sibling | 0.35 |
| [[bld_orchestration_output_validator]] | downstream | 0.34 |
| p01_kc_knowledge_best_practices | upstream | 0.30 |
