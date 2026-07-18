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
  - p06_bp_knowledge_card
  - bld_collaboration_prompt_cache
  - p01_kc_creation_best_practices
  - p01_kc_caching
  - int_ep08_exchange
  - prompt-cache-builder
  - revision_loop_policy_anuncio
  - response_format_anuncio_md
  - int_ep07_git_intelligence
---
## Resumo
Knowledge cards destilam o conhecimento de domínio em fatos atômicos de alta densidade. O gate de qualidade primário é densidade >= 0.80 -- a razão entre conteúdo informativo e total de palavras. O caminho mais confiável para alta densidade é estrutural: substituir prosa por bullets, substituir descrições por tabelas, e eliminar toda linguagem de enchimento.
## Padrão
Técnicas de aumento de densidade (aplique nesta ordem):
1. **Prosa -> bullets** - Converta cada parágrafo em uma lista de bullets. Cada bullet = um fato. Se um bullet precisar de um subfato, use um bullet aninhado, não uma frase composta.
2. **Descrições -> tabelas** - Converta qualquer comparação, enumeração ou mapeamento em uma tabela markdown. Tabelas carregam ~3x mais informação por linha em comparação com a prosa.
3. **Remova transições** - Apague: "como podemos ver", "vale notar que", "em resumo", "este documento", "o seguinte". Isso não agrega nenhuma informação.
4. **Tamanho do bullet** - Cada bullet com menos de 80 caracteres. Se ultrapassar, divida em dois bullets ou use uma tabela.
5. **Formato de axioma** - Todo axioma deve ser um imperativo começando com SEMPRE ou NUNCA. Não "caching é importante", mas "SEMPRE declare o TTL ao fazer cache, NUNCA faça cache sem expiração".
Regras de frontmatter:
- `quality: null` sempre -- a pontuação é externa, nunca autoatribuída
- o slug do `id` usa underscores: `p01_kc_topic_name`
- `tags` como lista YAML, não como string separada por vírgulas
- Nenhum caminho contendo `records/`, `.claude/`, `/home/`, `C:\` em qualquer lugar do card
Restrições de tamanho do corpo: mínimo 200 bytes (4+ seções com 3+ linhas cada), máximo 5KB.
## Anti-Padrão
- Parágrafos em prosa -- a densidade cai abaixo de 0.70 imediatamente.
- Bullets com mais de 80 caracteres -- o validador S10 detecta e força reformatação.
- Axioma como observação: "O caching melhora a performance" -- deve ser "SEMPRE declare o TTL do cache".
- `quality: 8.5` -- o validador H05 rejeita qualquer valor não nulo.
- `tags: "ai, ml, cache"` como string -- o validador H07 rejeita, precisa ser lista YAML.
- Caminhos internos em qualquer campo -- o validador H09 rejeita, quebra a portabilidade.
- tldr autorreferente: "Este card descreve caching" -- o tldr deve ser o fato direto, não uma descrição do card.
## Contexto


## Log de Produção

- [20260331_214115] PASS kind=knowledge_card retries=0 gates=6/6

- [20260331_214308] PASS kind=knowledge_card retries=0 gates=6/6

## Fronteira

Learning record persistente. NÃO é session_state (efêmero) nem axiom (imutável, não aprende).


## Função no Pipeline 8F

Função primária: **INJECT**


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[prompt_template_bullets_anuncio]] | upstream | 0.26 |
| [[p06_bp_knowledge_card]] | upstream | 0.20 |
| [[bld_collaboration_prompt_cache]] | downstream | 0.18 |
| [[p01_kc_creation_best_practices]] | upstream | 0.18 |
| [[p01_kc_caching]] | upstream | 0.17 |
| [[int_ep08_exchange]] | upstream | 0.16 |
| [[prompt-cache-builder]] | related | 0.16 |
| [[revision_loop_policy_anuncio]] | downstream | 0.16 |
| [[response_format_anuncio_md]] | upstream | 0.15 |
| [[int_ep07_git_intelligence]] | upstream | 0.15 |
