---
agent: pesquisa
pillar: P08
pillar_name: architecture
lang: pt-BR
source: api/core/pesquisas_executor.py (_run_pesquisa_v2); api/core/pesquisa_planner.py; api/core/pesquisa_retriever.py; api/core/pesquisa_synthesizer.py
fidelity: full
cexai_reference_kind: workflow + diagram + decision_record + workflow_primitive
cexai_source_of_truth: cexai/p08_wf_pesquisa_pipeline.md + cexai/p08_wp_parallel_retrieval.md + cexai/p08_dr_tier_router_decision.md
---

# P08 -- Arquitetura do Pipeline

Como o agente raciocina de ponta a ponta. Esta secao reconcilia o bundle ao
**pipeline de producao real** (codigo vivo). A producao roda 3 modulos em
sequencia, cobrindo 7 estagios:

```
PLANNER (estagios 1-2)  ->  RETRIEVER (estagios 3-4)  ->  SYNTHESIZER (estagios 5-7)
```

> Espelho CONVENTION-friendly de [[p08_wf_pesquisa_pipeline]] +
> [[p08_wp_parallel_retrieval]] + [[p08_dr_tier_router_decision]].

## Pipeline de producao (referencia -- o que o backend faz)

| # | Estagio | Modulo | O que faz |
|---|---------|--------|-----------|
| 1 | Intent classification | `pesquisa_planner` | Detecta preset; estima complexidade. |
| 2 | Query planning (STORM) | `pesquisa_planner` | Gera 5-7 sub-perguntas de 5 perspectivas; roteia fontes. |
| 3 | Parallel retrieval + CRAG | `pesquisa_retriever` | Chama TODAS as fontes em paralelo, avalia qualidade. |
| 4 | Entity resolution | `pesquisa_retriever` | Deduplica listings por hash de titulo. |
| 5 | Multi-criteria scoring | `pesquisa_synthesizer` | Pontua listings (7 dimensoes Gartner). |
| 6 | Synthesis | `pesquisa_synthesizer` | LLM funde tudo em mercado/concorrentes/tendencias. |
| 7 | Verification (CRITIC) | `pesquisa_synthesizer` | Valida coerencia, calcula `validation_score`. |

### Fontes do retriever na producao (substituidas em v2)
- **Inbound (marketplace):** mercadolivre, shopee, amazon, magalu, americanas
  (Serper + enriquecimento Firecrawl), exa, vision E2B.
- **Outbound (social):** youtube, reddit, reclameaqui, twitter, google_trends,
  gemini_search, openai_search.

## Pipeline EFETIVO no bundle codexa-v2 (degradado parcialmente, recuperado em ~95%)

No GPT autocontido nao ha retriever proprio. O estagio 3 colapsa em
**coleta humana assistida** (P04 TIER 1) + **3 actions** (P04 TIER 3a/b/c)
+ **sintese local**. Resultam 5 estagios bem definidos:

```
[1] GERACAO DE QUERIES         (planner estagios 1-2 -> puro raciocinio, porta 100%)
       v
[2] COLETA DE MARKETPLACE      (retriever estagio 3)
       |   - TIER 1 paste (default)
       |   - TIER 3: brave_search + firecrawl (parallel fan-out, NOVO v2)
       v   - CRAG-lite scoring per retrieval (NOVO v2)
[3] ANALISE DE CONCORRENTES    (retriever estagio 4 + synthesizer estagio 5)
       |   dedup + ranking + framework de gaps
       v   - TIER 3c tavily enrichment para reviews (NOVO v2)
[4] TAXONOMIA DE SEO           (synthesizer estagio 6 -> sintese local)
       v   - TIER 3c tavily topic=news para trends (NOVO v2)
[5] SINTESE + CRITIC VERIFY    (synthesizer estagios 6-7 -> P07)
       v   - CRITIC verify post-synthesis (NOVO v2)
   RELATORIO + HANDOFF JSON (P05), com self-check ([[p07_bl_pesquisa_self_check]])
```

## Mapeamento estagio-de-producao -> bundle codexa-v2

| Estagio producao | No bundle codexa-v2 |
|------------------|---------------------|
| 1 intent_classification | Inferir preset/categoria no Intake. |
| 2 query_planning (STORM) | Estagio 1 -- geracao de queries multi-perspectiva. |
| 3 parallel_retrieval | TIER 1 (paste) OU TIER 3 actions (brave+firecrawl+tavily em paralelo, NOVO v2). |
| 4 entity_resolution | Dedup manual ao consolidar a tabela de benchmark. |
| 5 multi_criteria_scoring (7 dim) | Ranking simples por vendas/reviews/nota/preco + CRAG-lite (NOVO v2). |
| 6 synthesis | Estagio 4-5 + montagem do relatorio. |
| 7 verification (CRITIC) | CRITIC verify (NOVO v2 -- agora explicito) + self-check do P07. |

## Workflow primitive: parallel retrieval (NOVO v2)

Source typed: [[p08_wp_parallel_retrieval]].

Estagio 2 fan-out:

```
                 +----> brave_search (SERP enumeration)   --+
                 |                                          |
[input: query]   +----> firecrawl (deep page extraction)  -+----> [merge + dedup]
                 |                                          |
                 +----> tavily (review/trend context) ------+
```

- Max parallel calls: 3
- Per-provider timeout: 30s
- Aggregate timeout: 45s
- Failure handling: continue with remaining providers; surface in `data_sources`

## Logica de decisao (tier router) -- NOVO em v2

Source typed: [[p04_ss_tier_router]] + [[p08_dr_tier_router_decision]].

- **Preset / marketplaces:** infira o preset (como o planner) e use os
  marketplaces que o usuario pedir; default = os 5. Tempo curto -> priorize
  **Mercado Livre** + **Shopee**.
- **Quantos concorrentes:** minimo 3, ideal 5. Pare em 5 (retorno decrescente).
- **Tier de coleta:** decision tree por fase (ver tabela em [[p04_ss_tier_router]]).
- **Quando escalar:** se nenhum concorrente cumpre criterios (>100 reviews,
  >4.5, selo), relaxe para o melhor disponivel e **sinalize** a decisao.
- **Estado entre estagios:** cada estagio consome a saida do anterior
  (queries -> coleta -> concorrentes -> SEO). Ver P10 (memoria).
- **NOVO v2:** session cache (P10) evita re-fetches; CRAG-lite (P07) rejeita
  retrievals fracos antes de entrarem na sintese.

## Principio de honestidade arquitetural

Onde o backend coletava por retriever + Firecrawl automatico, no bundle o
dado entra por **coleta humana assistida** (TIER 1 paste) ou **3 actions**
(TIER 3). O agente NUNCA simula um retriever que nao corre: ou le o que foi
colado/raspado, ou pede o dado ao usuario. A qualidade do output e funcao
direta de quantos anuncios reais foram conferidos, e cada numero carrega sua
origem (P04, matriz de rastreio).

## Decision record (preserva o WHY)

Source typed: [[p08_dr_tier_router_decision]]. O design v2 escolheu 3
providers + tier router para fechar 95% do gap de fidelidade (vs 30% se
mantivessemos so firecrawl). Esse record documenta as alternativas
consideradas e por que option C venceu.

## Diagrama de sequencia (didatico, para /teach)

```
User       Agent       brave_search   firecrawl      tavily         User
  |          |              |             |             |             |
  | product  |              |             |             |             |
  |--------->|              |             |             |             |
  |          | generate queries           |             |             |
  |          |---queries-+   |             |             |             |
  |          |           |   |             |             |             |
  |          | SERP enum |   |             |             |             |
  |          |--site:ML--->  |             |             |             |
  |          |<-20 URLs------+             |             |             |
  |          |              |             |             |             |
  |          | top 3 deep extract         |             |             |
  |          |---------url1--------------->             |             |
  |          |<-markdown1------------------+             |             |
  |          |---------url2--------------->             |             |
  |          |<-markdown2------------------+             |             |
  |          |              |             |             |             |
  |          | review context per comp 1                |             |
  |          |--------query "comp1 reviews"------------->             |
  |          |<-reviews_summary-------------------------+             |
  |          |              |             |             |             |
  |          | CRAG-lite + CRITIC                       |             |
  |          | synthesize + self-check                  |             |
  |  report  |              |             |             |             |
  |<---------|              |             |             |             |
```

## Related CEXAI artifacts

- [[workflow-builder]] -- stage-based execution graph
- [[diagram-builder]] -- architecture diagram artifact
- [[decision-record-builder]] -- ADR-style decision log
- [[workflow-primitive-builder]] -- primitive node for workflows
