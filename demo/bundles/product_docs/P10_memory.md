---
id: p10_lr_knowledge_card_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-03-27
updated: 2026-03-27
author: builder_agent
observation: "Knowledge_cards com densidade de corpo abaixo de 0.80 (razão entre conteúdo informativo e total de palavras) falham no gate de densidade e exigem reescrita. Bullets com mais de 80 caracteres são pegos pelo validador e forçam reformatação. Frases de enchimento ('este documento descreve', 'vale notar') consomem tokens sem agregar informação e são a principal causa de pontuações baixas de densidade. Axiomas escritos como observações ('caching melhora a performance') em vez de regras ('SEMPRE declare o TTL do cache, NUNCA faça cache sem expiração') são rejeitados pelo S18. Cards que referenciam caminhos internos do sistema falham no H09."
pattern: "Alcance densidade >= 0.80 fazendo: substituir parágrafos em prosa por listas de bullets, substituir descrições por tabelas comparativas, remover todas as frases de transição, garantir que cada bullet contenha exatamente um fato. Os axiomas devem ser imperativos SEMPRE/NUNCA, não observações. O campo quality deve ser null -- a pontuação é externa. Tamanho de corpo mínimo 200 bytes, máximo 5KB. Sem caminhos internos em nenhum campo."
evidence: "11 produções de knowledge_card: 6 falharam na primeira checagem de densidade (densidade média 0.64). ..."
confidence: 0.75
outcome: SUCCESS
domain: knowledge_card
tags: [knowledge-card, density, axioms, frontmatter, atomic-facts, classification]
tldr: "Densidade >= 0.80 exige bullets em vez de prosa e tabelas em vez de descrições. Axiomas são regras SEMPRE/NUNCA, não observações. quality:null sempre."
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
  - p01_kc_creation_best_practices
  - bld_collaboration_prompt_cache
  - p01_kc_caching
  - revision_loop_policy_anuncio
  - prompt-cache-builder
  - response_format_anuncio_md
  - scoring_rubric_anuncio_5d
  - p01_kc_lp01_knowledge
---
## Resumo
Knowledge_cards destilam conhecimento de domínio em fatos atômicos de alta densidade. O gate de qualidade primário é densidade >= 0.80 -- a razão entre conteúdo informativo e total de palavras. O caminho mais confiável para alta densidade é estrutural: substituir prosa por bullets, substituir descrições por tabelas, e eliminar toda linguagem de enchimento.
## Padrão
Técnicas de aumento de densidade (aplique nesta ordem):
1. **Prosa -> bullets** - Converta todo parágrafo em uma lista de bullets. Cada bullet = um fato. Se um bullet precisar de um subfato, use um bullet aninhado, não uma frase composta.
2. **Descrições -> tabelas** - Converta qualquer comparação, enumeração ou mapeamento em uma tabela markdown. Tabelas carregam ~3x mais informação por linha do que a prosa.
3. **Remova transições** - Elimine: "como podemos ver", "vale notar", "em resumo", "este documento", "a seguir". Isso não agrega informação alguma.
4. **Tamanho do bullet** - Cada bullet com menos de 80 caracteres. Se passar, divida em dois bullets ou use uma tabela.
5. **Formato do axioma** - Todo axioma deve ser um imperativo começando com SEMPRE ou NUNCA. Não "caching é importante" mas "SEMPRE declare o TTL ao fazer cache, NUNCA faça cache sem expiração".
Regras de frontmatter:
- `quality: null` sempre -- a pontuação é externa, nunca autoatribuída
- o slug de `id` usa underscores: `p01_kc_topic_name`
- `tags` como lista YAML, não string separada por vírgulas
- Nenhum caminho contendo `records/`, `.claude/`, `/home/`, `C:\` em nenhum lugar do card
Restrições de tamanho de corpo: mínimo 200 bytes (4+ seções com 3+ linhas cada), máximo 5KB.
## Antipadrão
- Parágrafos em prosa -- a densidade cai abaixo de 0.70 imediatamente.
- Bullets com mais de 80 caracteres -- o validador S10 pega e força reformatação.
- Axioma como observação: "Caching melhora a performance" -- deve ser "SEMPRE declare o TTL do cache".
- `quality: 8.5` -- o validador H05 rejeita qualquer valor diferente de null.
- `tags: "ai, ml, cache"` como string -- o validador H07 rejeita, deve ser lista YAML.
- Caminhos internos em qualquer campo -- o validador H09 rejeita, quebra a portabilidade.
- tldr autorreferente: "Este card descreve caching" -- o tldr deve ser o fato direto, não uma descrição do card.
## Contexto


## Registro de Produção

- [20260331_214115] PASS kind=knowledge_card retries=0 gates=6/6

- [20260331_214308] PASS kind=knowledge_card retries=0 gates=6/6

## Fronteira

Learning_record persistente. NÃO é session_state (efêmero) nem axiom (imutável, não aprende).


## Função no Pipeline 8F

Função primária: **INJECT**

## Artefatos Relacionados

| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[prompt_template_bullets_anuncio]] | a montante | 0.26 |
| [[p06_bp_knowledge_card]] | a montante | 0.21 |
| [[p01_kc_creation_best_practices]] | a montante | 0.18 |
| [[bld_collaboration_prompt_cache]] | a jusante | 0.18 |
| [[p01_kc_caching]] | a montante | 0.18 |
| [[revision_loop_policy_anuncio]] | a jusante | 0.17 |
| [[prompt-cache-builder]] | relacionado | 0.17 |
| [[response_format_anuncio_md]] | a montante | 0.17 |
| [[scoring_rubric_anuncio_5d]] | a montante | 0.16 |
| [[p01_kc_lp01_knowledge]] | a montante | 0.15 |
