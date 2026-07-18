---
id: p10_lr_knowledge_card_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-03-27
updated: 2026-03-27
author: builder_agent
observation: "Knowledge cards com densidade de corpo abaixo de 0.80 (razão entre conteúdo informativo e total de palavras) falham no gate de densidade e exigem reescrita. Bullets com mais de 80 caracteres são pegos pelo validador e forçam reformatação. Frases de enchimento ('this document describes', 'it is worth noting') consomem tokens sem agregar informação e são a causa primária de notas de densidade baixas. Axiomas escritos como observações ('caching melhora performance') em vez de regras ('SEMPRE declare o TTL do cache, NUNCA faça cache sem expiração') são rejeitados pelo S18. Cards que referenciam caminhos internos do sistema falham no H09."
pattern: "Alcance densidade >= 0.80 assim: substituindo parágrafos em prosa por listas de bullets, substituindo descrições por tabelas comparativas, removendo todas as frases de transição, garantindo que cada bullet contenha exatamente um fato. Os axiomas devem ser imperativos ALWAYS/NEVER, não observações. O campo quality deve ser null -- a pontuação é externa. Tamanho do corpo: 200 bytes no mínimo, 5KB no máximo. Sem caminhos internos em nenhum campo."
evidence: "11 produções de knowledge card: 6 falharam na primeira checagem de densidade (densidade média 0.64). ..."
confidence: 0.75
outcome: SUCCESS
domain: knowledge_card
tags: [knowledge-card, density, axioms, frontmatter, atomic-facts, classification]
tldr: "Densidade >= 0.80 exige bullets em vez de prosa e tabelas em vez de descrições. Axiomas são regras ALWAYS/NEVER, não observações. quality:null sempre."
impact_score: 7.5
decay_rate: 0.05
agent_group: edison
keywords: [knowledge_card, density, axiom, frontmatter, bullet, table, tldr, domain, meta, quality_null]
memory_scope: project
observation_types: [user, feedback, project, reference]
llm_function: INJECT
quality: null
title: "ISO de Memória - knowledge_card"
8f: "F7_govern"
density_score: 0.95
related:
  - prompt_template_bullets_anuncio
  - p06_bp_knowledge_card
  - p01_kc_creation_best_practices
  - bld_collaboration_prompt_cache
  - p01_kc_caching
  - prompt-cache-builder
  - revision_loop_policy_anuncio
  - p01_kc_artifact_quality_evaluation_methods
  - p01_kc_prompt_cache
---
## Resumo
Knowledge cards destilam conhecimento de domínio em fatos atômicos de alta densidade. O gate de qualidade primário é densidade >= 0.80 -- a razão entre conteúdo informativo e total de palavras. O caminho mais confiável para alta densidade é estrutural: substituir prosa por bullets, substituir descrições por tabelas, e eliminar toda linguagem de enchimento.
## Padrão
Técnicas de aumento de densidade (aplique em ordem):
1. **Prosa -> bullets** - Converta todo parágrafo em uma lista de bullets. Cada bullet = um fato. Se um bullet precisa de um subfato, use um bullet aninhado, não uma frase composta.
2. **Descrições -> tabelas** - Converta qualquer comparação, enumeração, ou mapeamento em uma tabela markdown. Tabelas carregam ~3x mais informação por linha que a prosa.
3. **Remova transições** - Apague: "as we can see", "it is worth noting", "in summary", "this document", "the following". Elas não agregam informação nenhuma.
4. **Tamanho do bullet** - Cada bullet com menos de 80 caracteres. Se passar disso, divida em dois bullets ou use uma tabela.
5. **Formato do axioma** - Todo axioma deve ser um imperativo começando com ALWAYS ou NEVER. Não "caching é importante" mas "SEMPRE declare o TTL ao fazer cache, NUNCA faça cache sem expiração".
Regras de frontmatter:
- `quality: null` sempre -- a pontuação é externa, nunca autoatribuída
- o slug do `id` usa underscores: `p01_kc_topic_name`
- `tags` como lista YAML, nunca como string separada por vírgula
- Nenhum caminho contendo `records/`, `.claude/`, `/home/`, `C:\` em nenhum lugar do card
Restrições de tamanho do corpo: mínimo 200 bytes (4+ seções com 3+ linhas cada), máximo 5KB.
## Antipadrão
- Parágrafos em prosa -- a densidade cai abaixo de 0.70 imediatamente.
- Bullets com mais de 80 caracteres -- o validador S10 pega e força reformatação.
- Axioma como observação: "caching melhora a performance" -- deve ser "SEMPRE declare o TTL do cache".
- `quality: 8.5` -- o validador H05 rejeita qualquer valor não nulo.
- `tags: "ai, ml, cache"` como string -- o validador H07 rejeita, precisa ser lista YAML.
- Caminhos internos em qualquer campo -- o validador H09 rejeita, quebra a portabilidade.
- tldr autorreferente: "this card describes caching" -- o tldr deve ser o fato direto, não uma descrição do card.
## Contexto


## Log de Produção

- [20260331_214115] PASS kind=knowledge_card retries=0 gates=6/6

- [20260331_214308] PASS kind=knowledge_card retries=0 gates=6/6

## Delimitação

Learning_record persistente. NÃO é session_state (efêmero) nem axiom (imutável, não aprende).


## Função no Pipeline 8F

Função primária: **INJECT**


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[prompt_template_bullets_anuncio]] | upstream | 0.25 |
| [[p06_bp_knowledge_card]] | upstream | 0.21 |
| [[p01_kc_creation_best_practices]] | upstream | 0.18 |
| [[bld_collaboration_prompt_cache]] | downstream | 0.18 |
| [[p01_kc_caching]] | upstream | 0.18 |
| [[prompt-cache-builder]] | related | 0.18 |
| [[revision_loop_policy_anuncio]] | downstream | 0.15 |
| [[p01_kc_artifact_quality_evaluation_methods]] | upstream | 0.15 |
| [[p01_kc_prompt_cache]] | related | 0.15 |
