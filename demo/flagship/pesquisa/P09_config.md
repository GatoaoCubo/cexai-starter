---
agent: pesquisa
pillar: P09
pillar_name: config
lang: pt-BR
source: api/core/pesquisas_executor.py (MARKETPLACE_URLS); api/v1/pesquisas.py (defaults); codexa-v2 audit secao 1 P09
fidelity: full
cexai_reference_kind: env_config + secret_config + rate_limit_config + feature_flag + constraint_spec
cexai_source_of_truth: cexai/p09_ec_marketplaces.md + cexai/p09_sc_api_keys.md + cexai/p09_rl_action_quotas.md + cexai/p09_ff_action_toggles.md + cexai/p09_cs_query_constraints.md
---

# P09 -- Configuracao (parametros, constraints, defaults)

> Espelho CONVENTION-friendly dos 5 typed artifacts em `cexai/` para P09.
> v2 adiciona gestao formal de API keys + rate limits + feature flags.

## Defaults

| Parametro | Default |
|-----------|---------|
| `marketplaces` | `["mercadolivre","shopee","amazon","magalu","americanas"]` |
| `target_audience` | "geral" |
| `price_range` | "nao especificado" |
| Moeda | BRL (R$) |
| Idioma das queries | PT-BR **sem acento** |
| Idioma do relatorio | PT-BR **com acento** |
| Tier default | TIER 1 paste (always-free) |

## Constraints de geracao de query

Source: [[p09_cs_query_constraints]]

| Constraint | Valor |
|------------|-------|
| Head terms | 10-15 |
| Longtails | 30-50 |
| Sinonimos | 15-25 |
| SEO inbound (total) | 100-150 |
| SEO outbound (total) | 50-80 |
| Negative keywords | 20-30 |
| Acentuacao nas queries | PROIBIDA (padrao de marketplace) |

## Criterios de selecao de concorrente

| Criterio | Limite |
|----------|--------|
| Quantidade de reviews | **> 100** |
| Nota (rating) | **> 4.5** |
| Sinal de venda | selo "Mais vendido" / "Best seller" / "Recomendado" |
| Relevancia | match DIRETO do produto (nao acessorio/correlato) |
| Quantidade de concorrentes | 3-5 |

## Parametros por marketplace

Source: [[p09_ec_marketplaces]]

| Marketplace | Chave (`marketplaces`) | Chave (`marketplace_data`) | URL de busca |
|-------------|------------------------|----------------------------|--------------|
| Mercado Livre | `mercadolivre` | `mercado_livre` | `https://lista.mercadolivre.com.br/{query}` |
| Shopee | `shopee` | `shopee` | `https://shopee.com.br/search?keyword={query}` |
| Amazon BR | `amazon` | `amazon_br` | `https://www.amazon.com.br/s?k={query}` |
| Magalu | `magalu` | `magalu` | `https://www.magazineluiza.com.br/busca/{query}/` |
| Americanas | `americanas` | `americanas` | `https://www.americanas.com.br/busca/{query}` |

> Formatacao da query na URL: minusculas, sem acento, espacos -> `+`.

## API Keys (NOVO em v2) -- env var pattern, NUNCA inline

Source: [[p09_sc_api_keys]]

| Provider | Env var | Como obter | Free tier |
|----------|--------|-----------|-----------|
| firecrawl | `${FIRECRAWL_API_KEY}` | firecrawl.dev -> API Keys (formato `fc-...`) | 500 credits/mo |
| brave_search | `${BRAVE_API_KEY}` | api.search.brave.com -> Get Started (formato `BSA...`) | 2000 queries/mo |
| tavily | `${TAVILY_API_KEY}` | tavily.com -> Get Free API Key (formato `tvly-...`) | 1000 queries/mo |

### Per-runtime delivery

| Runtime | Como entregar a chave |
|---------|---------------------|
| Custom GPT FULL | UI Actions: Authentication tab (por action) |
| Projects ENXUTO | N/A -- Projects nao tem Actions |
| Claude Projects | `.mcp.json` env block |
| Gemini Gems | Gemini extension config (best-effort) |

### Regras de seguranca (NAO NEGOCIAVEIS)

1. NUNCA inline uma chave real em qualquer arquivo do bundle.
2. NUNCA committe uma chave no repositorio.
3. Documente APENAS o nome da env var (`${FIRECRAWL_API_KEY}`), nunca o valor.
4. Chaves do usuario ficam com o usuario (Custom GPT roda em secure store da OpenAI).

## Rate limits (NOVO em v2)

Source: [[p09_rl_action_quotas]]

| Provider | Quota free | Burn medio por pesquisa | Pesquisas/mes (free) |
|----------|-----------|------------------------|----------------------|
| firecrawl | 500 credits/mo | 3-5 scrapes | 100 |
| brave_search | 2000 queries/mo | 5 SERP queries | 400 |
| tavily | 1000 queries/mo | 2-3 research queries | 333 |

Bottleneck combinado (free tier): ~100 pesquisas/mes, limitado por firecrawl.
Cache (P10) estende este numero para ~200-300 quando ha re-references.

### Handling de rate limit

| Status | Provider | Acao |
|--------|----------|------|
| 429 | qualquer | Wait 60s; retry 1x; depois fallback chain |
| 402 | firecrawl | Credit esgotado; fallback chain para tavily extract |
| 401 | qualquer | Surface error com chave em questao |

## Feature flags (NOVO em v2)

Source: [[p09_ff_action_toggles]]

| Flag | Default | Efeito quando false |
|------|---------|---------------------|
| `enable_firecrawl` | true (se chave presente) | Skip firecrawl; fall para TIER 1 paste |
| `enable_brave` | true (se chave presente) | Skip brave; URLs SERP devem vir de paste do usuario |
| `enable_tavily` | true (se chave presente) | Skip tavily; review/trend context inferido ou omitido |
| `enable_tier1_paste_default` | true | TIER 1 paste sempre default; setando false forca TIER 3 |

Como o usuario seta:
- Custom GPT FULL: no campo Instructions ou per-conversation prefix
- Projects ENXUTO: N/A (flags fixos -- TIER 1 only)
- Claude Projects: `.mcp.json` env block (`PESQUISA_ENABLE_FIRECRAWL=false`)
- Gemini Gems: instrucao manual no Gem prompt

## Quality gate (ver P07)
- Aceite: `quality_score >= 8.0`
- Escalacao: `< 7.5`
- Max. iteracoes de autocorrecao: 3

## Onde estavam os dados na pagina (selectors -- REFERENCIA historica)

O backend usava estes seletores CSS para extrair dados automaticamente. Aqui
servem so como **mapa de onde olhar** na leitura manual:

- **Titulo**: `h2`, `.ui-search-item__title`, `.product-card__title`, `.product-name`
- **Preco**: `.price-tag-fraction`, `.ui-search-price__second-container`, `.price-template__text`, `.priceSales`
- **Nota/avaliacoes**: `.ui-search-reviews__rating-number`, `.review-stars`, `.rating-value`

> Esses seletores NAO sao executados -- o scraping nao porta. Sao pista visual
> de onde o preco/titulo/nota costumam aparecer.

## Related CEXAI artifacts

- [[env-config-builder]] -- environment-scoped config
- [[secret-config-builder]] -- credential management config
- [[rate-limit-config-builder]] -- throughput throttling policy
- [[feature-flag-builder]] -- runtime toggle definition
- [[constraint-spec-builder]] -- declarative constraint set
