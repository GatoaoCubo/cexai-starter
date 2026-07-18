---
id: p10_lr_knowledge_card_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-03-27
updated: 2026-03-27
author: builder_agent
observation: "Knowledge cards com densidade de corpo abaixo de 0.80 (razao entre conteudo informativo e total de palavras) falham no portao de densidade e precisam ser reescritos. Bullets com mais de 80 caracteres sao pegos pelo validador e forcam reformatacao. Frases de enchimento ('este documento descreve', 'vale notar que') consomem tokens sem adicionar informacao e sao a causa principal de pontuacao de densidade baixa. Axiomas escritos como observacao ('caching melhora performance') em vez de regra ('SEMPRE declare o TTL do cache, NUNCA cacheie sem expiracao') sao rejeitados pelo S18. Cards que referenciam caminhos internos do sistema falham no H09."
pattern: "Alcance densidade >= 0.80 assim: troque paragrafos de prosa por listas de bullets, troque descricoes por tabelas comparativas, remova todas as frases de transicao, garanta que cada bullet contenha exatamente um fato. Os axiomas precisam ser imperativos SEMPRE/NUNCA, nao observacoes. O campo quality precisa ser null -- a pontuacao e sempre externa. Corpo com no minimo 200 bytes, no maximo 5KB. Nenhum caminho interno em nenhum campo."
evidence: "11 producoes de knowledge_card: 6 falharam na primeira checagem de densidade (densidade media de 0.64). ..."
confidence: 0.75
outcome: SUCCESS
domain: knowledge_card
tags: [knowledge-card, density, axioms, frontmatter, atomic-facts, classification]
tldr: "Densidade >= 0.80 exige bullets em vez de prosa e tabelas em vez de descricao. Axiomas sao regras SEMPRE/NUNCA, nao observacoes. quality:null sempre."
impact_score: 7.5
decay_rate: 0.05
agent_group: edison
keywords: [knowledge_card, density, axiom, frontmatter, bullet, table, tldr, domain, meta, quality_null]
memory_scope: project
observation_types: [user, feedback, project, reference]
llm_function: INJECT
quality: null
title: "ISO de Memoria: knowledge_card"
8f: "F7_govern"
density_score: 0.95
related:
  - prompt_template_bullets_anuncio
  - p06_bp_knowledge_card
  - p01_kc_creation_best_practices
  - scoring_rubric_anuncio_5d
  - response_format_anuncio_md
  - prompt_template_description_anuncio
  - revision_loop_policy_anuncio
  - bld_knowledge_card_knowledge_card
---
## Resumo
Knowledge cards destilam conhecimento de dominio em fatos atomicos de alta densidade. O portao de qualidade principal e densidade >= 0.80 -- a razao entre conteudo informativo e total de palavras. O caminho mais confiavel para densidade alta e estrutural: trocar prosa por bullets, trocar descricao por tabela, e eliminar toda linguagem de enchimento.
## Padrao
Tecnicas de aumento de densidade (aplicar nesta ordem):
1. **Prosa -> bullets** - Converta todo paragrafo em uma lista de bullets. Cada bullet = um fato. Se um bullet precisar de um subfato, use um bullet aninhado, nunca uma frase composta.
2. **Descricoes -> tabelas** - Converta qualquer comparacao, enumeracao ou mapeamento em uma tabela markdown. Tabelas carregam ~3x mais informacao por linha do que a prosa.
3. **Remova transicoes** - Apague: "como podemos ver", "vale notar que", "em resumo", "este documento", "o seguinte". Isso nao adiciona informacao nenhuma.
4. **Tamanho do bullet** - Cada bullet com menos de 80 caracteres. Se passar disso, divida em dois bullets ou use uma tabela.
5. **Formato do axioma** - Todo axioma precisa ser um imperativo comecando com SEMPRE ou NUNCA. Nao "caching e importante", e sim "SEMPRE declare o TTL ao cachear, NUNCA cacheie sem expiracao".
Regras de frontmatter:
- `quality: null` sempre -- a pontuacao e externa, nunca auto-atribuida
- o slug do `id` usa underscores: `p01_kc_topic_name`
- `tags` como lista YAML, nunca como string separada por virgula
- nenhum caminho contendo `records/`, `.claude/`, `/home/`, `C:\` em lugar nenhum do card
Restricoes de tamanho de corpo: minimo 200 bytes (4+ secoes com 3+ linhas cada), maximo 5KB.
## Anti-Padrao
- Paragrafos de prosa -- a densidade cai abaixo de 0.70 imediatamente.
- Bullets com mais de 80 caracteres -- o validador S10 pega e forca reformatacao.
- Axioma como observacao: "Caching melhora performance" -- o correto e "SEMPRE declare o TTL do cache".
- `quality: 8.5` -- o validador H05 rejeita qualquer valor diferente de null.
- `tags: "ai, ml, cache"` como string -- o validador H07 rejeita, precisa ser lista YAML.
- Caminhos internos em qualquer campo -- o validador H09 rejeita, quebra a portabilidade.
- tldr autorreferente: "Este card descreve caching" -- o tldr precisa ser o fato direto, nao uma descricao do card.
## Contexto

Padrao observado durante producoes reais do knowledge-card-builder (ver Registro de
Producao abaixo). A maioria dos cards que falhou na primeira tentativa tinha o corpo
predominantemente em prosa; a correcao estrutural (bullets + tabelas) resolveu a
maioria dos casos sem precisar de uma segunda rodada de F6 PRODUCE.

## Registro de Producao

- [20260331_214115] PASS kind=knowledge_card retries=0 gates=6/6

- [20260331_214308] PASS kind=knowledge_card retries=0 gates=6/6

## Fronteira

Learning record persistente. NAO e session_state (efemero) nem axiom (imutavel, nao aprende).


## Funcao no Pipeline 8F

Funcao primaria: **INJECT**


## Related Artifacts

| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[prompt_template_bullets_anuncio]] | upstream | 0.26 |
| [[p06_bp_knowledge_card]] | upstream | 0.21 |
| [[p01_kc_creation_best_practices]] | upstream | 0.20 |
| [[scoring_rubric_anuncio_5d]] | upstream | 0.19 |
| [[response_format_anuncio_md]] | upstream | 0.19 |
| [[prompt_template_description_anuncio]] | upstream | 0.18 |
| [[revision_loop_policy_anuncio]] | downstream | 0.17 |
| [[bld_knowledge_card_knowledge_card]] | upstream | 0.16 |
