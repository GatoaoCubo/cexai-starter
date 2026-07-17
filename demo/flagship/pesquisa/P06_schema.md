---
agent: pesquisa
pillar: P06
pillar_name: schema
lang: pt-BR
source: api/v1/pesquisas.py (PesquisaRequest, MercadoResponse, ConcorrentesResponse, TendenciasResponse)
fidelity: full
cexai_reference_kind: input_schema + interface + openapi_spec
cexai_source_of_truth: cexai/p06_if_handoff_to_anuncio.md + actions/firecrawl_action.yaml + actions/brave_search_action.yaml + actions/tavily_search_action.yaml
---

# P06 -- Schemas de Entrada e Saida

> Espelho CONVENTION-friendly de [[p06_if_handoff_to_anuncio]] +
> as 3 specs OpenAPI em `actions/`. Schema de I/O com novidade v2: campo
> `data_sources` aceita os 3 action providers (firecrawl/brave/tavily).

## Entrada (PesquisaRequest)

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `product_name` | string | **SIM** | Produto a pesquisar. Ex.: "creme hidratante facial". |
| `category` | string | nao | Categoria. Se vazia, o agente infere a partir do nome. |
| `target_audience` | string | nao | Publico-alvo. Ex.: "mulheres 25-45 anos". Default: "geral". |
| `price_range` | string | nao | Faixa de preco esperada. Ex.: "R$ 50-150". |
| `marketplaces` | array | nao | Default: `["mercadolivre","shopee","amazon","magalu","americanas"]`. |
| `tier_preferences` | object | nao (NOVO em v2) | Toggles por TIER: `enable_firecrawl`, `enable_brave`, `enable_tavily`. |

### Validacao de entrada
- Se faltar `product_name`: **pergunte ao usuario** antes de prosseguir (campo unico obrigatorio).
- Se `category` vazia: infira e **confirme** a categoria inferida com o usuario.
- `marketplaces` aceita: `mercadolivre`, `shopee`, `amazon`, `magalu`, `americanas`.
- `tier_preferences` defaults: todos true se chaves presentes; todos false se chaves ausentes.

## Saida -- tres blocos (nomes de campo EXATOS do codigo de producao)

> Fonte: `api/v1/pesquisas.py` (MercadoResponse / ConcorrentesResponse /
> TendenciasResponse). Os campos `execution_time_ms`, `mock` e
> `marketplaces_failed` sao do envelope de producao -- no bundle preencha
> conforme indicado.

### MercadoResponse (pesquisa de mercado) -- `/mercado`
| Campo | Tipo | No bundle |
|-------|------|-----------|
| `head_terms` | list[str] | gerado |
| `longtails` | list[str] | gerado |
| `synonyms` | list[str] \| dict | gerado |
| `marketplace_data` | dict | so com dado COLETADO (paste/browsing/firecrawl/brave/tavily) |
| `price_analysis` | dict (min, max, avg, currency) | calculado do coletado |
| `quality_score` | float (0-10) | = validation_score |
| `execution_time_ms` | int | opcional; 0 se nao medir |
| `mock` | bool | **sempre `false`** -- voce nao gera dado falso |
| `marketplaces_failed` | list[str] | marketplaces sem dado coletado |

### ConcorrentesResponse (analise de concorrentes) -- `/concorrentes`
| Campo | Tipo | No bundle |
|-------|------|-----------|
| `competitors` | list[dict] -- name, url, marketplace, price, reviews_count, rating, strengths, weaknesses, gaps | de dado coletado |
| `benchmark` | dict | consolidado do coletado |
| `gaps` | list[str] | derivado |
| `opportunities` | list[str] | derivado |
| `quality_score` | float (0-10) | = validation_score |
| `execution_time_ms` | int | opcional |
| `mock` | bool | **sempre `false`** |

### TendenciasResponse (taxonomia/tendencias) -- `/tendencias`
| Campo | Tipo | No bundle |
|-------|------|-----------|
| `seo_inbound` | list[str] | gerado |
| `seo_outbound` | list[str] | gerado |
| `negative_keywords` | list[str] | gerado |
| `category_paths` | dict | do coletado / inferido (marque inferencia) |
| `trends` | dict | so se coletado; senao `{}`. NOVO em v2: pode conter dados de tavily topic=news |
| `quality_score` | float (0-10) | = validation_score |
| `execution_time_ms` | int | opcional |
| `mock` | bool | **sempre `false`** |

## OpenAPI specs (3 actions, NOVO em v2)

| Action | OpenAPI spec | Endpoint | Auth |
|--------|-------------|----------|------|
| firecrawl | `actions/firecrawl_action.yaml` | POST /v1/scrape + POST /v1/extract | Bearer ${FIRECRAWL_API_KEY} |
| brave_search | `actions/brave_search_action.yaml` | GET /res/v1/web/search | X-Subscription-Token: ${BRAVE_API_KEY} |
| tavily | `actions/tavily_search_action.yaml` | POST /search | api_key in body: ${TAVILY_API_KEY} |

## Regras de schema

1. Nomes de campo sao FIXOS (nao traduza chaves JSON -- `head_terms`, nao `termos_principais`).
2. `marketplace_data` usa chaves: `mercado_livre`, `shopee`, `amazon_br`, `magalu`, `americanas`.
3. `quality_score`/`validation_score` e float 0-10; reflita a completude e a confiabilidade dos dados coletados.
4. Listas/objetos vazios sao validos quando o dado nao foi coletado -- **preferivel a inventar**.
5. `mock` e SEMPRE `false`: o bundle nunca emite dado sintetico rotulado como real. `marketplaces_failed` lista os marketplaces que ficaram sem dado coletado (honestidade de cobertura).
6. NOVO v2: `data_sources` enum agora inclui `firecrawl`, `brave`, `tavily` alem de `paste`, `browsing`, `user`, `estimado`.

## Anti-alucinacao no schema (OBRIGATORIO)

A maior falha de um GPT autocontido e **preencher campo com numero inventado**.
Regras de preenchimento, sem excecao (especializacao para pesquisa em P11):

1. **Fonte de verdade = dado coletado.** So preencha `price`, `sold_quantity`,
   `rating_count`, `rating_average`, `name` (concorrente) e qualquer numero de
   mercado com valor que veio de **paste / browsing / firecrawl / brave /
   tavily / user** (ver P04).
2. **Proibido fabricar:** preco, unidades vendidas, no de avaliacoes, nota,
   nomes de concorrentes, tamanho de mercado, % de share, faturamento.
3. **Lacuna -> pergunte OU marque, nunca invente.** Campo obrigatorio faltando:
   uma pergunta objetiva ao usuario, ou placeholder `[A CONFIRMAR: <campo>]`.
4. **Toda metrica carrega origem** (P04, matriz de rastreio).
5. **Estimativa != fato.** Se precisar estimar uma faixa, rotule explicitamente
   como `estimado` e registre no bloco de suposicoes (P05/P07).

## Referencias cruzadas

- Handoff interface canonica: [[p06_if_handoff_to_anuncio]]
- Action specs OpenAPI: [[p04_st_firecrawl]] / [[p04_st_brave_search]] / [[p04_st_tavily]]
- Anti-hallucination guardrail (P11): [[p11_gr_anti_hallucination_pesquisa]]

## Related CEXAI artifacts

- [[input-schema-builder]] -- typed input contract
- [[interface-builder]] -- integration contract
- [[openapi-spec-builder]] -- OpenAPI surface declaration
