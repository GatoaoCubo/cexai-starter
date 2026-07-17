---
agent: pesquisa
pillar: P10
pillar_name: memory
lang: pt-BR
source: records/pool/workflows/fat/FAT_001..._SELF_CONTAINED.md ($variables entre STEPs); api/core/pesquisas_executor.py (handoff/estado)
fidelity: full
cexai_reference_kind: memory_summary + entity_memory + prompt_cache
cexai_source_of_truth: cexai/p10_pc_url_scrape_cache.md
---

# P10 -- Contexto e Memoria (estado entre estagios)

O agente e um pipeline sequencial: cada estagio produz variaveis que o
proximo consome. Mantenha esse estado vivo dentro da conversa.

> Espelho CONVENTION-friendly. Novidade v2: cache de URL scrape para evitar
> re-fetches em fases posteriores (estende quota free tier). Source typed:
> [[p10_pc_url_scrape_cache]].

## Variaveis de estado (carregadas estagio a estagio)

| Variavel | Produzida em | Consumida por |
|----------|--------------|---------------|
| `product_name`, `category`, `target_audience`, `price_range`, `marketplaces` | Entrada | Todos |
| `tier_preferences` (NOVO v2) | Entrada | Estagio 2 (tier router) |
| `head_terms`, `longtails`, `synonyms` | Estagio 1 | Estagios 2-4, handoff |
| `marketplace_data`, `price_analysis` (min/max/sweet_spot) | Estagio 2 | Estagios 3-4, handoff |
| `competitors`, `benchmark` | Estagio 3 | Estagio 4, gaps |
| `gaps`, `opportunities` | Estagio 3 | Posicionamento, handoff (pain_points/desired_gains) |
| `seo_inbound`, `seo_outbound`, `negative_keywords`, `category_paths` | Estagio 4 | Handoff |
| `data_sources` (origem por metrica/marketplace) | Estagios 2-3 (coleta) | JSON de handoff, bloco de suposicoes |
| `marketplaces_failed` (sem dado coletado) | Estagio 2 | Output final, suposicoes |
| `validation_score` | Self-check (P07) | Output final |
| `url_scrape_cache` (NOVO v2) | Estagio 2 | Estagios 3-4 (re-references gratuitas) |

## URL scrape cache (NOVO v2)

Source typed: [[p10_pc_url_scrape_cache]]

Cache de URL fetches escopado a uma conversa. Evita re-scraping da mesma URL
quando o usuario referencia em estagios subsequentes (e.g. estagio 2 extrai,
estagio 3 deep-dive, estagio 4 SEO usa titles).

| Field | Valor |
|-------|-------|
| Cache key | `(provider, url)` |
| TTL | 3600s (1 hora) |
| Storage | Conversation memory (sem DB externo) |
| Eviction | LRU; max 50 entradas |

### Quando o cache HIT

| Estagio | Pattern de hit |
|---------|----------------|
| 2 marketplace_analysis | Primeira fetch -> MISS; popula cache |
| 3 competitor_research | Re-referencia mesma URL -> HIT; salva 1 firecrawl credit |
| 4 seo_taxonomy | Puxa titles de competitors cacheados -> HIT |

### Quando o cache MISS (forca re-fetch)

- Usuario pede "refresh competitor X"
- TTL expirou (>1h)
- CRAG-lite score < 5.0 (scrape ruim; resultado anterior nao trustworthy)

## O que rastrear na conversa

1. **Inputs confirmados**: produto + categoria validados com o usuario (nao repergunte).
2. **Anuncios ja coletados**: guarde titulo/preco/reviews/nota/vendas de cada concorrente conferido + a ORIGEM (`paste`/`browsing`/`firecrawl`/`brave`/`tavily`/`user`).
3. **Decisoes tomadas**: ex. "relaxei o criterio de reviews porque nenhum concorrente passava de 100" -- registre e mostre.
4. **Lacunas pendentes**: dados que faltam coletar (vao para `[A CONFIRMAR]` / `estimado` e para o bloco de suposicoes) + `marketplaces_failed`.
5. **Action quotas consumidas** (NOVO v2): registre quantas chamadas de firecrawl/brave/tavily foram feitas -- ajuda o usuario a entender custo + se aproxima do limite free tier.

## Handoff (memoria que sai do agente)

Ao final, o estado consolida no bloco HANDOFF (ver P05 + [[p06_if_handoff_to_anuncio]]).
Esse e o "save" do agente -- o que o proximo agente (anuncio) recebe:

```yaml
head_terms / longtails / synonyms
pain_points:    derivados de gaps
desired_gains:  derivados de opportunities
price_recommendation: do price_analysis (sweet spot)
```

## Regras de memoria

- NAO reperguntar o que ja foi confirmado (produto, categoria, marketplaces).
- Persistir numeros coletados; nunca recalcular a partir de dado inventado.
- Se a conversa for retomada, peca o ultimo relatorio/handoff para restaurar
  o estado -- o bundle nao tem banco de dados (a persistencia de DB do backend
  NAO porta).
- NOVO v2: ao retomar uma pesquisa, o cache de URL e perdido (escopo de
  conversacao). Document o trade-off com o usuario.

## Related CEXAI artifacts

- [[memory-summary-builder]] -- compressed memory rollup
- [[entity-memory-builder]] -- persistent entity store
- [[prompt-cache-builder]] -- prompt-response cache layer
