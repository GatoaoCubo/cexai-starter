---
kind: config
id: bld_config_knowledge_card
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
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
title: "Config Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Golden and anti-examples for knowledge card construction, demonstrating ideal structure and common pitfalls."
domain: "knowledge card construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, knowledge card construction, config knowledge card, knowledge_card, builder, examples, "p01_kc_{topic_slug}.md"]
density_score: 0.90
related:
  - bld_config_output_validator
---
# Config: Regras de Producao do knowledge_card
## Convencao de Nomenclatura
| Escopo | Convencao | Exemplo |
|-------|-----------|---------|
| Arquivos de artefato | `p01_kc_{topic_slug}.md` | `p01_kc_prompt_caching.md` |
| Diretorio do builder | kebab-case | `knowledge-card-builder/` |
| Campos de frontmatter | snake_case | `density_score`, `when_to_use` |
| Slug do topico | minusculas, underscores | `rag_fundamentals`, `prompt_caching` |
Regra: o id DEVE ser igual ao nome-base do arquivo (o validador verifica isso em H02).
## Caminhos de Arquivo
- Saida: `cex/P01_knowledge/examples/p01_kc_{topic}.md`
- Compilado: `cex/P01_knowledge/compiled/p01_kc_{topic}.yaml`
## Limites de Tamanho (alinhado com o SCHEMA)
- Corpo: 200-5120 bytes (validador H08)
- Total (frontmatter + corpo): maximo ~6500 bytes
- Densidade: >= 0.80
- Bullet maximo: 80 caracteres (validador S10)
- Title: 5-100 caracteres (validador S03)
- tldr: <= 160 caracteres, sem autorreferencias (S01, S02)
## Requisitos do Corpo
- >= 4 secoes (validador S06)
- Cada secao >= 3 linhas nao vazias (validador S08)
- A maior secao >= 30% do corpo (validador S07)
- >= 1 tabela (S11), >= 1 bloco de codigo (S12), >= 1 URL (S13)
## Selecao do Tipo de KC
| Conteudo | Tipo | Estrutura de Corpo |
|---------|------|---------------|
| Tecnologia externa (APIs, padroes) | domain_kc | Referencia Rapida + Conceitos + Fases + Regras + Fluxo + Comparativo + Referencias |
| Interno a CEX (arquitetura) | meta_kc | Resumo + Especificacao + Padroes + Antipadroes + Aplicacao + Referencias |
Padrao: domain_kc. Use meta_kc somente para documentacao interna do sistema CEX.
## Atualidade
- o campo updated deve refletir a ultima edicao significativa
- o conhecimento se degrada mais devagar que model_cards (sem gate hard de 90 dias)
- KCs desatualizados sao identificados pelo ranking de atualidade do brain_query

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_config_output_validator]] | irmao | 0.35 |
| [[bld_orchestration_output_validator]] | a jusante | 0.34 |
| p01_kc_knowledge_best_practices | a montante | 0.30 |
