---
id: p10_lr_knowledge_card_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-03-27
updated: 2026-03-27
author: builder_agent
observation: "Knowledge cards with body density below 0.80 (ratio of informative content to total words) fail the density gate and require rewrite. Bullets over 80 characters are caught by validator and force reformatting. Filler phrases ('this document describes', 'it is worth noting') consume tokens without adding information and are the primary cause of low density scores. Axioms written as observations ('caching improves performance') instead of rules ('ALWAYS declare cache TTL, NEVER cache without expiry') are rejected by S18. Cards referencing internal system paths fail H09."
pattern: "Achieve density >= 0.80 by: replacing prose paragraphs with bullet lists, replacing descriptions with comparison tables, removing all transition sentences, ensuring each bullet contains exactly one fact. Axioms must be ALWAYS/NEVER imperatives, not observations. Quality field must be null — scoring is external. Body size 200 bytes minimum, 5KB maximum. No internal paths in any field."
evidence: "11 knowledge card productions: 6 failed first density check (avg density 0.64). ..."
confidence: 0.75
outcome: SUCCESS
domain: knowledge_card
tags: [knowledge-card, density, axioms, frontmatter, atomic-facts, classification]
tldr: "Density >= 0.80 requires bullets over prose and tables over descriptions. Axioms are ALWAYS/NEVER rules, not observations. quality:null always."
impact_score: 7.5
decay_rate: 0.05
agent_group: edison
keywords: [knowledge_card, density, axiom, frontmatter, bullet, table, tldr, domain, meta, quality_null]
memory_scope: project
observation_types: [user, feedback, project, reference]
llm_function: INJECT
quality: null
title: Memory ISO - knowledge_card
8f: "F7_govern"
density_score: 0.95
related:
  - prompt_template_bullets_anuncio
  - prompt-cache-builder
  - bld_collaboration_prompt_cache
  - n00_prompt_cache_manifest
  - p01_kc_creation_best_practices
  - bld_knowledge_card_prompt_cache
  - ex_knowledge_card_prompt_caching
  - p08_pat_caching_strategy
  - bld_tools_prompt_cache
  - p06_bp_knowledge_card
---
## Resumo
Artefatos knowledge_card destilam conhecimento de dominio em fatos atomicos de alta densidade. O principal gate de qualidade e densidade >= 0.80 -- a razao entre conteudo informativo e total de palavras. O caminho mais confiavel para alta densidade e estrutural: substituir prosa por bullets, substituir descricoes por tabelas, e eliminar toda linguagem de enchimento.
## Padrao
Tecnicas de aumento de densidade (aplicar em ordem):
1. **Prosa -> bullets** - Converta cada paragrafo em uma lista de bullets. Cada bullet = um fato. Se um bullet precisar de um subfato, use um bullet aninhado, nao uma frase composta.
2. **Descricoes -> tabelas** - Converta qualquer comparacao, enumeracao ou mapeamento em uma tabela markdown. Tabelas carregam ~3x mais informacao por linha do que prosa.
3. **Remova transicoes** - Elimine: "como podemos ver", "vale notar", "em resumo", "este documento", "a seguir". Elas nao agregam nenhuma informacao.
4. **Tamanho do bullet** - Cada bullet com menos de 80 caracteres. Se ultrapassar, divida em dois bullets ou use uma tabela.
5. **Formato do axioma** - Todo axioma deve ser um imperativo comecando com ALWAYS ou NEVER. Nao "cache e importante" mas "ALWAYS declare o TTL ao usar cache, NEVER faca cache sem expiracao".
Regras de frontmatter:
- `quality: null` sempre -- a pontuacao e externa, nunca autoatribuida
- o slug do `id` usa underscores: `p01_kc_topic_name`
- `tags` como lista YAML, nao como string separada por virgulas
- Nenhum caminho contendo `records/`, `.claude/`, `/home/`, `C:\` em nenhum lugar do card
Restricoes de tamanho do corpo: minimo 200 bytes (4+ secoes com 3+ linhas cada), maximo 5KB.
## Antipadrao
- Paragrafos em prosa -- a densidade cai abaixo de 0.70 imediatamente.
- Bullets com mais de 80 caracteres -- o validador S10 detecta e forca reformatacao.
- Axioma como observacao: "Cache melhora a performance" -- deve ser "ALWAYS declare o TTL do cache".
- `quality: 8.5` -- o validador H05 rejeita qualquer valor diferente de null.
- `tags: "ai, ml, cache"` como string -- o validador H07 rejeita, deve ser lista YAML.
- Caminhos internos em qualquer campo -- o validador H09 rejeita, quebra a portabilidade.
- tldr autorreferente: "Este card descreve cache" -- o tldr deve ser o fato direto, nao uma descricao do card.
## Contexto


## Log de Producao

- [20260331_214115] PASS kind=knowledge_card retries=0 gates=6/6

- [20260331_214308] PASS kind=knowledge_card retries=0 gates=6/6

## Fronteira

Registro de aprendizado persistente. NAO e session_state (efemero) nem axiom (imutavel, nao aprende).


## Funcao no Pipeline 8F

Funcao primaria: **INJECT**

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[prompt_template_bullets_anuncio]] | a montante | 0.26 |
| [[prompt-cache-builder]] | relacionado | 0.24 |
| [[bld_collaboration_prompt_cache]] | a jusante | 0.23 |
| [[n00_prompt_cache_manifest]] | relacionado | 0.19 |
| [[p01_kc_creation_best_practices]] | a montante | 0.19 |
| [[bld_knowledge_card_prompt_cache]] | a montante | 0.18 |
| [[ex_knowledge_card_prompt_caching]] | a montante | 0.18 |
| [[p08_pat_caching_strategy]] | a montante | 0.18 |
| [[bld_tools_prompt_cache]] | a montante | 0.18 |
| [[p06_bp_knowledge_card]] | a montante | 0.17 |
