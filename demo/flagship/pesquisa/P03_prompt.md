---
agent: pesquisa
pillar: P03
pillar_name: prompt
lang: pt-BR
source: records/pool/workflows/fat/FAT_001_FAT_ADW_PESQUISA_COMPLETA_SELF_CONTAINED.md (STEP 1-4)
fidelity: full
cexai_reference_kind: prompt_template + chain + reasoning_strategy
cexai_source_of_truth: cexai/p03_pt_query_generation.md + cexai/p03_ch_pesquisa_full.md
---

# P03 -- Receitas de Prompt (templates por estagio)

Os "como gerar" textuais de cada estagio do pipeline. Estes templates portam
100% (sao logica generativa, nao dependem de backend).

> Espelho CONVENTION-friendly dos typed artifacts em `cexai/`:
> [[p03_pt_query_generation]] + [[p03_pt_marketplace_analysis]] +
> [[p03_pt_competitor_research]] + [[p03_pt_seo_taxonomy]] + [[p03_ch_pesquisa_full]].

## Estagio 1 -- Geracao de Queries

### Regras (inquebraveis)
1. **Portugues BR** apenas.
2. **SEM acento** nas queries de busca (padrao de marketplace). Ex.: "garrafa termica", nunca "garrafa termica" com acento.
3. Incluir **modificadores de compra**: `comprar`, `preco`, `promocao`, `barato`, `frete gratis`.
4. Incluir **modificadores de atributo**: tamanhos, cores, materiais, capacidade, voltagem.

### Tipos de query a gerar
- **Head terms (10-15)**: nome primario do produto, termos de categoria, descritores genericos. Ex.: "garrafa termica", "squeeze", "copo termico".
- **Longtails (30-50)**: head term + atributo + uso/dor. Ex.: "garrafa termica 500ml academia", "squeeze que nao vaza", "copo termico inox cafe".
- **Sinonimos (15-25)**: variacoes regionais, coloquiais, alternativas sem marca. Ex.: "tumbler", "caneca termica", "copo stanley".

### Template
```
A partir de product_name + category + atributos conhecidos, gere:
- head_terms[10-15]
- longtails[30-50]
- synonyms[15-25]
Todas SEM acento, em PT-BR, com modificadores de compra e atributo.
```

## Estagio 2 -- Analise de Marketplace

```
Para cada marketplace selecionado (ML, Shopee, Amazon BR, Magalu, Americanas):
1. Colete os top 3-5 anuncios via P04 (TIER 1 paste e o default; URLs de busca em P01).
2. Se TIER 3b brave habilitado: enumere primeiro via brave_search e firecrawl os top 3 (TIER 3a).
3. Registre por anuncio: titulo, preco, vendas, qtd_reviews, rating, vendedor, diferenciais + ORIGEM do dado (paste/browsing/action/user).
4. Calcule price_analysis (min, max, media, sweet_spot) so sobre o dado coletado; lacuna = [A CONFIRMAR], nunca inventada.
5. Anote patterns: keywords comuns no titulo, estrutura do titulo, padrao de bullets.
```

## Estagio 3 -- Analise de Concorrentes

```
Selecione 3-5 concorrentes que atendam aos criterios (P06/P09):
  qtd_reviews > 100  E  rating > 4.5  E  selo de venda  E  match direto do produto.
Para cada um, extraia:
- basic: nome, marketplace, preco, reviews, rating
- copy_analysis: keywords do titulo, qtd de bullets, tamanho da descricao,
  gatilhos psicologicos, claims unicos
- visual_analysis: qtd de imagens, razao lifestyle/produto, tem infografico?
- gaps: beneficios ausentes, pontos fracos, areas de oportunidade
- Se TIER 3c tavily habilitado: enriqueca com contexto de reviews
  (reclameaqui/reddit) via tavily query "<nome do produto> reviews".
Consolide: benchmark (agregado), gaps (consolidados), opportunities (priorizadas).
```

### Raciocinio de gaps -> oportunidades
- Um **gap** e algo que o lider NAO faz bem (ex.: nenhum concorrente mostra a tampa em close, ninguem cita "nao vaza", descricoes genericas).
- Cada gap vira uma **oportunidade** acionavel (ex.: "destacar vedacao anti-vazamento no titulo e na 1a imagem").

## Estagio 4 -- Taxonomia de SEO

```
A partir das queries + dados de concorrentes, monte:
- seo_inbound (100-150 keywords) por intencao:
    high_intent: "[produto] comprar", "[produto] preco", "[produto] promocao"
    mid_intent:  "[produto] e bom", "[produto] vale a pena", "[produto] review"
    low_intent:  "melhor [categoria]", "[categoria] qualidade"
- seo_outbound (50-80 keywords) para midia paga: exact / phrase / broad match
- negative_keywords (20-30): marcas concorrentes, termos irrelevantes,
  sinais de baixa qualidade
- category_paths: caminho de categoria por marketplace
- Se TIER 3c tavily habilitado: enriqueca com topic=news para trend signal
  (busca "<categoria> tendencias 2026" em [g1.globo.com, exame.com]).
```

## Estagio 5 -- Sintese + Self-Check

Ver typed artifacts:
- [[p07_qg_pesquisa_gate]] (5-dim rubric + 8.0 gate)
- [[p07_lj_crag_lite]] (per-retrieval CRAG-lite scoring)
- [[p07_jc_critic_verify]] (CRITIC post-synthesis verify)
- [[p07_bl_pesquisa_self_check]] (closed-loop, max 3 iterations)

## Estagio 6 -- Entrega + Handoff

Ver typed artifact [[p05_fm_pesquisa_report]] (Markdown report format) +
[[p06_if_handoff_to_anuncio]] (handoff JSON schema) +
[[p12_hp_pesquisa_to_anuncio]] (handoff protocol).

## Related CEXAI artifacts

- [[prompt-template-builder]] -- parameterized prompt contract
- [[chain-builder]] -- ordered prompt composition
- [[reasoning-strategy-builder]] -- reasoning-pattern selector
