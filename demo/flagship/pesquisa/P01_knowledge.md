---
agent: pesquisa
pillar: P01
pillar_name: knowledge
lang: pt-BR
source: records/pool/workflows/fat/FAT_001_FAT_ADW_PESQUISA_COMPLETA_SELF_CONTAINED.md; api/core/pesquisas_executor.py
fidelity: full
cexai_reference_kind: knowledge_card
cexai_source_of_truth: cexai/p01_kc_pesquisa_marketplaces_br.md
---

# P01 -- Base de Conhecimento: Mercado E-commerce BR

Conhecimento que o agente de pesquisa precisa saber de cor para pesquisar mercado de e-commerce brasileiro. Fatos, taxonomias e regras dos marketplaces.

> Espelho CONVENTION-friendly do typed artifact [[p01_kc_pesquisa_marketplaces_br]] (em `cexai/`).

## Os 5 marketplaces brasileiros (perfil)

| Marketplace | Perfil | Publico | Posicionamento |
|-------------|--------|---------|----------------|
| **Mercado Livre** | Maior e mais competitivo. Mais SKUs, mais reviews, busca dominante. | Amplo, todas as classes | Volume + reputacao (MercadoLider) |
| **Shopee** | Sensivel a preco, frete gratis agressivo, gamificacao. | Mais jovem, classe C/D | Menor preco, cupons |
| **Amazon BR** | Premium, vantagem Prime, foco em logistica. | Classe A/B, recorrente | Qualidade + entrega rapida |
| **Magalu (Magazine Luiza)** | Varejo tradicional digitalizado, marketplace + lojas fisicas. | Publico mais velho, interior | Confianca da marca, parcelamento |
| **Americanas** | Alcance amplo, foco em promocoes e datas comerciais. | Amplo | Promocao, sortimento |

> Cada marketplace tem ritmo de preco e estrutura de titulo diferente. O mesmo produto pode ter "sweet spot" (preco mais comum entre os campeoes de venda) distinto em cada um.

## URLs de busca por marketplace (REFERENCIA para pesquisa manual)

Use estes padroes para abrir buscas no navegador. Substitua `{query}` pela query SEM acento e com `+` no lugar de espaco.

| Marketplace | Padrao de URL de busca |
|-------------|------------------------|
| Mercado Livre | `https://lista.mercadolivre.com.br/{query}` |
| Shopee | `https://shopee.com.br/search?keyword={query}` |
| Amazon BR | `https://www.amazon.com.br/s?k={query}` |
| Magalu | `https://www.magazineluiza.com.br/busca/{query}/` |
| Americanas | `https://www.americanas.com.br/busca/{query}` |

> Exemplo: para "garrafa termica 500ml" no ML, abra
> `https://lista.mercadolivre.com.br/garrafa+termica+500ml`

## Onde encontrar cada dado na pagina (REFERENCIA -- leitura manual)

Ao abrir um anuncio, localize visualmente estes campos (a captura e manual, NAO automatizada):

| Dado | Onde procurar na pagina |
|------|--------------------------|
| **Titulo** | Cabecalho do anuncio (topo). No ML, o titulo completo costuma ter 60 caracteres. |
| **Preco** | Bloco de preco destacado, abaixo do titulo. Anote o preco cheio e o a vista/PIX. |
| **Avaliacoes (qtd)** | Numero de reviews ao lado das estrelas (ex.: "(1.247)"). |
| **Nota (rating)** | Media em estrelas, 0-5 (ex.: 4.7). |
| **Vendedor** | Nome da loja + reputacao. No ML procure selo "MercadoLider". |
| **Selos/badges** | "Mais vendido", "Recomendado", "Frete gratis", "Full". |

## Taxonomia de categorias (caminhos de exemplo)

Cada marketplace tem sua arvore de categorias. Registre o caminho da categoria do produto:

- Mercado Livre: `Casa, Moveis e Decoracao > Cozinha > Garrafas Termicas`
- Shopee: `Casa e Decoracao > Utensilios de Cozinha`
- Amazon BR: `Cozinha > Garrafas e Caixas Termicas`

> Categoria correta = mais relevancia organica. Sempre identifique o caminho usado pelos campeoes de venda, nao o que parece "logico".

## Conceitos-chave de SEO de marketplace

- **Head terms**: termos curtos e genericos do produto/categoria (alto volume, alta concorrencia). Ex.: "garrafa termica".
- **Longtails**: head term + atributo/uso/dor (menor volume, maior intencao e conversao). Ex.: "garrafa termica 500ml academia que nao vaza".
- **Sinonimos**: variacoes regionais e coloquiais. Ex.: "squeeze", "tumbler", "copo termico".
- **Intencao de compra (buying intent)**: modificadores que sinalizam decisao: "comprar", "preco", "promocao", "barato", "frete gratis".
- **Sweet spot de preco**: o preco mais frequente entre os anuncios campeoes -- nao a media simples, e sim a faixa que concentra os "Mais vendido".

## Tier de coleta -- mapa por TIER (CEXAI)

O agente coleta dados em 3 tiers (detalhe em `P04_tools.md` + typed artifact
[[p04_ss_tier_router]]). O retriever_config abaixo declara, por marketplace, quais
TIERs sao recomendados:

| Marketplace | TIER 1 paste | TIER 2 browsing | TIER 3a firecrawl | TIER 3b brave | TIER 3c tavily |
|-------------|-------------|-----------------|-------------------|---------------|---------------|
| Mercado Livre | preferido (anti-bot pesado) | parcial | bom (com waitFor=8000) | bom (SERP enum) | reviews via reclameaqui/reddit |
| Shopee | preferido | parcial | medio (anti-bot variavel) | bom | reviews via reddit |
| Amazon BR | preferido | parcial | bom | bom | reviews via reddit/youtube |
| Magalu | preferido | parcial | bom | bom | reviews via reclameaqui |
| Americanas | preferido | parcial | bom | bom | reviews via reclameaqui |

## Multi-runtime caveat (D6 -- 4 runtimes)

| Runtime | Acesso a P01 | Actions disponiveis |
|---------|-------------|---------------------|
| Custom GPT FULL | conhecimento completo (este arquivo) | 3 actions (firecrawl + brave + tavily) |
| ChatGPT Projects ENXUTO | conhecimento completo (folded em projects_free/P01) | NENHUMA -- TIER 1 paste only |
| Claude Projects | conhecimento completo (claude/knowledge/P01) | via MCP bridge configurado pelo usuario |
| Gemini Gems | conhecimento completo (gemini/knowledge/P01) | TIER 1 default; TIER 3 best-effort |

## Limitacao de fidelidade (honesta)

A versao de producao do pesquisa coleta os 5 marketplaces por um **retriever paralelo** (API do Mercado Livre + Serper + Firecrawl + Exa + busca social) no backend. Neste bundle isso NAO existe; em vez disso, a versao v2 oferece 3 actions opcionais (firecrawl + brave_search + tavily) que, juntas, recuperam ~95% da capacidade de producao. TIER 1 paste continua o default sempre-free. Ver P04 (ferramentas) e P11 (guardrails).

## Referencias cruzadas

- TIER 1 paste workflow: [[p04_ap_tier1_paste]]
- TIER 3 actions: [[p04_st_firecrawl]], [[p04_st_brave_search]], [[p04_st_tavily]]
- Tier router decision: [[p04_ss_tier_router]]
- Output handoff schema: [[p06_if_handoff_to_anuncio]]

## Related CEXAI artifacts

- [[knowledge-card-builder]] -- typed knowledge unit (KC)
