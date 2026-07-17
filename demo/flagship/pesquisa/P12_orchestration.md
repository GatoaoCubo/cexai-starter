---
agent: pesquisa
pillar: P12
pillar_name: orchestration
lang: pt-BR
source: api/core/pesquisas_executor.py (_run_pesquisa_v2 sequencial); api/core/pesquisa_planner.py / pesquisa_retriever.py / pesquisa_synthesizer.py
fidelity: full
cexai_reference_kind: workflow + chain + handoff_protocol + dispatch_rule
cexai_source_of_truth: cexai/p12_wf_pesquisa_loop.md + cexai/p12_hp_pesquisa_to_anuncio.md + cexai/p03_ch_pesquisa_full.md
---

# P12 -- Orquestracao (loop operacional passo a passo)

A sequencia exata que o agente executa em toda pesquisa. Espelha o pipeline
de producao (PLANNER -> RETRIEVER -> SYNTHESIZER), com a coleta automatica
substituida por TIER 1 paste (default) ou TIER 3 actions (NOVO v2).

> Espelho CONVENTION-friendly de [[p12_wf_pesquisa_loop]] +
> [[p12_hp_pesquisa_to_anuncio]] + [[p03_ch_pesquisa_full]].

## O loop operacional

```
[0] INTAKE  (= planner estagio 1: intent classification)
    - Receba product_name (obrigatorio). Se faltar, pergunte.
    - Infira o preset (inbound_marketplace / outbound_social / mixed /
      competitor_deep_dive) e a category; CONFIRME a category.
    - Confirme marketplaces (default: 5). Anote target_audience e price_range.
    - Pergunte qual TIER de coleta usar (default TIER 1 paste; TIER 3 se
      usuario configurou chaves). -> P04 / P06

[1] GERAR QUERIES  (= planner estagio 2: STORM)                  -> P03 estagio 1
    - head_terms (10-15), longtails (30-50), synonyms (15-25)
    - PT-BR, SEM acento, com modificadores de compra/atributo
    - VALIDAR (P07): faixas e ausencia de acento

[2] COLETAR DADOS DE MARKETPLACE  (= retriever estagio 3)        -> P04 + P09
    - TIER 1 (default): entregue as URLs de busca (P01/P09) e o template de
      coleta; o usuario abre 3-5 anuncios no navegador logado e cola os campos.
    - TIER 2 (se habilitado): tente web browsing; trate como PARCIAL.
    - TIER 3 (so Custom GPT FULL):
        - brave_search enumera SERP por marketplace (parallel, 5 queries)
        - usuario / agente escolhe top 3-5
        - firecrawl extrai cada uma (parallel)
        - CRAG-lite scoring per retrieval (NOVO v2)
    - Registre titulo/preco/vendas/reviews/nota/vendedor/selos + ORIGEM do dado.
    - Calcule price_analysis (min/max/sweet_spot). Sem dado -> [A CONFIRMAR].
    - NUNCA invente numero (P11).

[3] ANALISAR CONCORRENTES  (= retriever estagio 4 + synth estagio 5)  -> P03 estagio 3
    - Dedup manual; selecione 3-5 que cumpram criterios (>100 reviews, >4.5, selo)
    - Ranking simples por vendas/reviews/nota/preco
    - Por concorrente: copy_analysis, visual_analysis, gaps
    - TIER 3c tavily enrichment (NOVO v2): query "<comp> reviews"
      em [reclameaqui.com.br, reddit.com] -- contexto de review
    - Consolide benchmark; derive gaps -> opportunities

[4] MONTAR TAXONOMIA DE SEO  (= synthesizer estagio 6)           -> P03 estagio 4
    - seo_inbound (high/mid/low intent), seo_outbound (match types)
    - negative_keywords, category_paths por marketplace
    - TIER 3c tavily com topic=news opcional (NOVO v2): trend signal

[5] SINTETIZAR + AUTOAVALIAR  (= synthesizer estagios 6-7: CRITIC)  -> P05 + P07
    - Monte o relatorio Markdown (formato fixo) + bloco JSON de handoff
    - Rode CRITIC verify (NOVO v2); calcule validation_score
    - Anexe "## Suposicoes e dados a confirmar" (P07/P11)
    - Se < 8.0: resolva e repita (max 3); se < 7.5: escale

[6] ENTREGAR
    - Relatorio Markdown + JSON handoff + Confidence X.X/10
    - Sinalize "Pronto para Anuncio: SIM/NAO" e o que falta (se NAO)
```

## Encadeamento e dependencias

| Passo | Depende de | Entrega para |
|-------|------------|--------------|
| 1 Queries | Intake | 2, 3, 4, handoff |
| 2 Coleta marketplace | 1 (head_terms) + TIER (P04) | 3, 4 (price_analysis) |
| 3 Concorrentes | 2 (anuncios coletados) | 4, gaps -> oportunidades |
| 4 SEO | 1 + 3 | handoff |
| 5 Sintese | 1-4 | 6 |

## Modos de execucao (= endpoints da producao)

| Modo | Endpoint | Passos |
|------|----------|--------|
| Pesquisa completa (default) | `/generate/full` | 0-6 |
| So mercado | `/mercado` | 0-2 (MercadoResponse) |
| So concorrentes | `/concorrentes` | 0-3 (ConcorrentesResponse) |
| So tendencias/SEO | `/tendencias` | 0-1-4 (TendenciasResponse) |

## Handoff para a esteira codexa-v2

Source typed: [[p12_hp_pesquisa_to_anuncio]]

Ao terminar, o bloco HANDOFF (P05) e o contrato de saida para o proximo
agente: `pesquisa -> anuncio -> imagens`. Entregue head/longtails/synonyms,
pain_points (dos gaps), desired_gains (das oportunidades) e
price_recommendation (sweet spot). Cada dado mantem sua ORIGEM.

### Quando NAO firar o handoff
- validation_score < 7.5 (escalation threshold) -- escala ao usuario.
- `marketplaces_failed` cobre > 50% dos marketplaces solicitados -- peca
  TIER 1 paste primeiro.

### Como anuncio consome (mapping)

| Campo pesquisa | Como anuncio consome |
|----------------|--------------------|
| `head_terms[]` | Seed para geracao de titulo |
| `longtails[]` | SEO bullet/descricao |
| `synonyms[]` | Geracao de variantes A/B |
| `price_analysis.sweet_spot` | Faixa de preco sugerida |
| `competitors[].weaknesses[]` | Angulos de diferenciacao |
| `gaps[]` | Sementes de UVP (unique value proposition) |
| `opportunities[]` | Selecao de hero feature |
| `seo_inbound[]` | Bag de keywords de listing |
| `seo_outbound[]` | Seed de midia paga |
| `category_paths{}` | Assignment de categoria de marketplace |

## Tier escalation (NOVO v2) -- quando sugerir TIER 3 ao usuario

Source typed: [[p12_dr_tier_escalation]] (dispatch_rule)

- Se usuario tem chave configurada -> tier router escolhe TIER 3 quando apropriado.
- Se TIER 1 paste excede 5 concorrentes -> sugira "proxima vez, tente TIER 3 para economizar tempo".
- Se usuario pede explicit speed -> proponha setup de chave TIER 3.

## Logica de decisao

- **Preset / marketplaces:** infira o preset e use os marketplaces que o
  usuario pedir; default = 5. Tempo curto -> priorize ML + Shopee.
- **Quantos concorrentes:** minimo 3, ideal 5. Pare em 5 (retorno decrescente).
- **Tier de coleta:** TIER 1 default; TIER 3 se chaves; fallback chain
  ([[p04_fc_action_degradation]]) cobre falhas.
- **Quando escalar:** se nenhum concorrente cumpre criterios (>100 reviews,
  >4.5, selo), relaxe o criterio e **sinalize** a decisao.

## Related CEXAI artifacts

- [[workflow-builder]] -- stage-based execution graph
- [[chain-builder]] -- ordered prompt composition
- [[handoff-protocol-builder]] -- inter-agent handoff contract
- [[dispatch-rule-builder]] -- routing/dispatch rule
