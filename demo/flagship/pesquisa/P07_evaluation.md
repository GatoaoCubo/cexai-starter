---
agent: pesquisa
pillar: P07
pillar_name: evaluation
lang: pt-BR
source: records/pool/workflows/fat/FAT_001..._SELF_CONTAINED.md (Closed-Loop, quality_gate 8.0, validation criteria); codexa-v2 audit secao 1 (CRAG-lite + CRITIC additions)
fidelity: full
cexai_reference_kind: quality_gate + scoring_rubric + llm_judge + judge_config + bugloop
cexai_source_of_truth: cexai/p07_qg_pesquisa_gate.md + cexai/p07_lj_crag_lite.md + cexai/p07_jc_critic_verify.md + cexai/p07_bl_pesquisa_self_check.md
---

# P07 -- Quality Gates (autoavaliacao)

O agente reve o proprio trabalho antes de entregar (closed-loop). Gate de
aceite: **>= 8.0/10**. Novidades v2: CRAG-lite per-retrieval + CRITIC
verification post-synthesis.

> Espelho CONVENTION-friendly de [[p07_qg_pesquisa_gate]] + [[p07_lj_crag_lite]]
> + [[p07_jc_critic_verify]] + [[p07_bl_pesquisa_self_check]].

## Loop fechado (Request -> CRAG-lite -> Validate -> CRITIC -> Resolve)

```
[GERAR queries]
   v
[COLETAR via TIER 1/2/3]
   v
[CRAG-LITE per retrieval: relevance + freshness + extractability] (NOVO v2)
   v
[VALIDAR 5-dim rubric]
   v
[CRITIC verify post-synthesis] (NOVO v2)
   v
[score >= 8.0?] -> SIM -> entrega
            |
            v
        RESOLVER ----> (max 3 iter; se < 7.5 escala ao usuario)
```

- `max_iterations`: 3
- `quality_gate`: 8.0
- `escalation_threshold`: 7.5 (abaixo disso, pare e peca ajuda ao usuario)

## Rubrica de pontuacao (5 dimensoes, 0-10 cada)

| Dimensao | O que avalia | Peso |
|----------|--------------|------|
| **Cobertura de queries** | Head (10-15), longtails (30-50), sinonimos (15-25) nas faixas? Sem acento? | 20% |
| **Qualidade dos concorrentes** | 3-5 concorrentes que cumprem criterios (>100 reviews, >4.5, selo)? Dados reais/conferidos? | 25% |
| **Precisao de preco** | Min/max/sweet spot coerentes? Sweet spot != media ingenua? | 20% |
| **Acionabilidade de gaps** | Cada gap vira oportunidade concreta? Posicionamento claro? | 20% |
| **Integridade do SEO** | Inbound por intencao, outbound por match, negativas presentes, category paths? | 15% |

Score final = media ponderada. Reporte como `Confidence: X.X/10`.

## CRAG-lite (NOVO v2) -- per-retrieval scoring

Antes de qualquer dado entrar na sintese, cada resultado de TIER 3 e scored
em 3 dimensoes:

| Dimensao | 0-10 | O que checa |
|----------|-----|------------|
| Relevance | 0=irrelevante, 10=match exato | Pagina e o produto certo? |
| Freshness | 0=stale (>30d), 10=fresh (<7d) | Data dos dados |
| Extractability | 0=campos faltando, 10=todos presentes | Pegamos title + price + reviews + rating? |

Decisao por score:
- `>= 7.5` -> aceita; entra na sintese
- `5.0-7.4` -> aceita com downweighting; flag em `data_sources.<campo>.confidence`
- `< 5.0` -> REJEITA. Retry com outro action provider (fallback chain)
- `< 3.0` -> REJEITA + escala -- pede TIER 1 paste

Source typed: [[p07_lj_crag_lite]].

## CRITIC verify (NOVO v2) -- post-synthesis verification

Apos a sintese, antes de entregar, roda CRITIC:

| Check | O que verifica |
|-------|----------------|
| Coherence | Os gaps mapeiam para as opportunities? |
| Consistency | `price_analysis.sweet_spot` cabe em `marketplace_data.*.price_range`? |
| Completeness | 5 secoes do relatorio + handoff JSON presentes? |
| Anti-hallucination | Toda metrica tem origem em `data_sources`? mock false? |
| Cross-reference | SEO keywords conectam aos head_terms? |

Decisao por validation_score:
- `>= 8.0` -> publica (gate passa)
- `7.5-7.9` -> self-correct via bugloop (max 3 iter)
- `< 7.5` -> ESCALA -- entrega parcial + diz o que falta

Source typed: [[p07_jc_critic_verify]].

## GATE ANTI-ALUCINACAO (bloqueante -- revise ANTES de pontuar)

Esta e a checagem no 1. Especializacao do bloco da CONVENTION para pesquisa:

1. **Fonte de verdade = dado coletado** (paste / browsing / firecrawl / brave / tavily / user, P04).
   NUNCA invente preco, unidades vendidas, no de avaliacoes, nota, nome de
   concorrente, tamanho de mercado, share ou faturamento.
2. **Toda metrica do relatorio/JSON tem origem rastreavel.** Metrica sem origem
   = remova ou marque `[A CONFIRMAR]`. `data_sources` no JSON cobre cada campo.
3. **Lacuna -> pergunte OU marque, nunca preencha.** Use `[A CONFIRMAR: <campo>]`.
4. **Estimativa e rotulada `estimado`** e listada no bloco de suposicoes.
5. **Nunca afirme que houve scraping ao vivo SEM que a action tenha de fato corrido.**
   `mock` e sempre `false`.
6. **Auto-checagem item a item:** para CADA numero, pergunte "de onde isto veio?"
   Se a resposta nao for paste/browsing/firecrawl/brave/tavily/user -> nao e fato, e suposicao.

> Se qualquer numero nao passar neste gate, o `validation_score` cai e o item
> vira `[A CONFIRMAR]`. E preferivel um relatorio honesto e parcial a um completo
> e inventado.

## Checklist de self-check (antes de entregar)

- [ ] `product_name` confirmado e `category` validada com o usuario.
- [ ] Queries em PT-BR e **SEM acento**; com modificadores de compra.
- [ ] 3-5 concorrentes; cada um com preco, reviews, nota **conferidos** (origem `paste`/`browsing`/`firecrawl`/`brave`/`tavily`/`user`), nunca inventados.
- [ ] Nenhum numero fabricado -- dados `estimado` marcados; lacunas como `[A CONFIRMAR]`.
- [ ] Toda metrica tem origem em `data_sources`; `mock: false`; `marketplaces_failed` preenchido.
- [ ] `price_analysis` com min/max/sweet spot (so sobre dado coletado).
- [ ] Pelo menos 2 pares gap->oportunidade.
- [ ] SEO inbound + outbound + negativas + category paths preenchidos.
- [ ] Relatorio Markdown + bloco JSON de handoff (P05) ambos presentes.
- [ ] Bloco "## Suposicoes e dados a confirmar" presente no relatorio.
- [ ] `validation_score` declarado.
- [ ] (NOVO v2) CRAG-lite passou em todos os retrievals usados.
- [ ] (NOVO v2) CRITIC verify passou.

## Acoes de resolucao (quando score < 8.0)

- Cobertura de query baixa -> expandir longtails/sinonimos faltantes.
- Concorrentes fracos -> buscar substitutos que cumpram os criterios.
- Preco vago -> conferir mais 1-2 anuncios para fechar o sweet spot.
- Gaps genericos -> reescrever como oportunidade especifica e mensuravel.

> Se apos 3 iteracoes o score < 7.5: **escale** -- entregue o parcial e diga
> ao usuario exatamente quais dados faltam coletar.

## Council opt-in (F7c) -- opcional

`requires_council: false` por default. Usuarios podem ativar via flag em
`00_instructions` para consenso multi-LLM em casos contenciosos (e.g.
decisoes de posicionamento competitivo). Council = 3-4 juizes LLM
independentes de providers diferentes; divergence_score > 0.3 bloqueia
publicacao.

## Related CEXAI artifacts

- [[quality-gate-builder]] -- F7 GOVERN validation gate
- [[scoring-rubric-builder]] -- quality scoring criteria
- [[llm-judge-builder]] -- LLM-as-judge config
- [[judge-config-builder]] -- judge ensemble policy
- [[bugloop-builder]] -- auto-fix feedback loop
