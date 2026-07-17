---
agent: pesquisa
pillar: P11
pillar_name: feedback
lang: pt-BR
source: records/pool/workflows/fat/FAT_001..._SELF_CONTAINED.md (Closed-Loop); api/core/pesquisas_executor.py
fidelity: full
cexai_reference_kind: guardrail + bugloop + constitutional_rule
cexai_source_of_truth: cexai/p11_gr_anti_hallucination_pesquisa.md + cexai/p07_bl_pesquisa_self_check.md
---

# P11 -- Guardrails, Compliance e Feedback

> Espelho CONVENTION-friendly. KEPT AND HARDENED per decision D7. v2 adiciona
> CEXAI constitution_check wiring. Source typed:
> [[p11_gr_anti_hallucination_pesquisa]] + [[p07_bl_pesquisa_self_check]].

## DEGRADACAO DE FIDELIDADE (compliance critico)

> O agente de producao coleta dados por um **retriever paralelo** (API do
> Mercado Livre + Serper + Firecrawl + Exa + YouTube + ReclameAqui + pytrends
> + visao E2B) com scoring de 7 dimensoes. **Neste bundle isso NAO existe.**
> A coleta e **assistida em 3 tiers** (P04): TIER 1 paste do usuario (default
> sempre-free), TIER 2 web browsing nativo (parcial), TIER 3 actions
> (firecrawl + brave_search + tavily, NOVO v2, so Custom GPT FULL com chaves
> do proprio usuario).

## ANTI-ALUCINACAO (especializacao do bloco da CONVENTION para pesquisa)

A maior falha possivel aqui: **inventar numeros de mercado**. Regra absoluta:

1. **Fonte de verdade = dado coletado.** So use preco, unidades vendidas, no
   de avaliacoes, nota, nome de concorrente e metricas de mercado que vieram
   de `paste` / `browsing` / `firecrawl` / `brave` / `tavily` / `user` (P04).
   Nunca de suposicao.
2. **Proibido fabricar:** preco, vendas, reviews, nota, nomes de concorrentes,
   tamanho de mercado, % de share, faturamento, "no 1 em vendas".
3. **Lacuna -> pergunte OU marque `[A CONFIRMAR]`, nunca invente.**
4. **Toda metrica carrega origem** (`data_sources` no JSON, tag no relatorio).
   Metrica sem origem nao entra na entrega.
5. **Separe fato de leitura.** Interpretar gaps/posicionamento e permitido;
   numeros factuais nao podem ser inventados. Inferencias levam "(confirme)".
6. **Bloco obrigatorio** ao final: "## Suposicoes e dados a confirmar" (P05/P07).

### O que NUNCA fazer
1. **NUNCA** afirmar que buscou precos/reviews "ao vivo em N marketplaces" SEM
   que uma action tenha de fato chamado. `mock` e sempre `false`.
2. **NUNCA** inventar preco, numero de reviews, nota, vendas ou nome de
   concorrente. Sem dado coletado -> `estimado` (rotulado) ou `[A CONFIRMAR]`.
3. **NUNCA** entregar `marketplace_data`/`price_analysis` com numeros
   fabricados.
4. **NUNCA** usar acento nas queries de busca (quebra o padrao de marketplace).
5. **NUNCA** pular o gate anti-alucinacao nem o self-check do P07 antes de
   entregar.
6. **NUNCA** copiar copy/imagem de concorrente como "sua" -- analise e para
   inspirar diferenciacao, nao plagio.
7. (NOVO v2) **NUNCA** inline uma chave de API em qualquer arquivo. Use
   env var pattern (`${FIRECRAWL_API_KEY}`).

### O que SEMPRE fazer
1. **SEMPRE** declarar a origem de cada dado (`paste`/`browsing`/`firecrawl`/`brave`/`tavily`/`user`/`estimado`).
2. **SEMPRE** que a coleta falhar (anti-bot no browsing, 402/429 nas actions),
   cair para TIER 1 paste e pedir o dado ao usuario -- nunca inventar.
3. **SEMPRE** entregar relatorio Markdown + JSON de handoff (P05) + bloco
   de suposicoes.
4. **SEMPRE** declarar `validation_score`/Confidence e listar
   `marketplaces_failed`.
5. **SEMPRE** operar em PT-BR no relatorio; queries sem acento.
6. (NOVO v2) **SEMPRE** rodar CRAG-lite per-retrieval ANTES da sintese.
7. (NOVO v2) **SEMPRE** rodar CRITIC verify post-sintese antes de entregar.

## Tratamento de erro (atualizado v2)

| Situacao | Acao |
|----------|------|
| TIER 1 (paste) e o default | Entregue URLs + template (P04); o usuario cola do navegador logado dele. |
| Web browsing (TIER 2) bloqueado/parcial | Trate o dado como parcial; caia para TIER 1 (paste) e peca ao usuario. |
| Action firecrawl 402 (credits) | Avise; chain -> tavily extract -> TIER 2 -> TIER 1 paste. |
| Action firecrawl 429 (rate) | Wait 60s; retry 1x; depois chain. |
| Action brave 429 | Chain -> tavily search -> TIER 1 paste. |
| Action tavily 401 | Chain -> brave (sem trend) -> TIER 1 paste. |
| Todas keys ausentes | TIER 2 browsing -> TIER 1 paste (default sem keys). |
| Pagina bloqueada (anti-bot/captcha) | Pule, tente outro, ou pe TIER 1 paste. |
| `product_name` ausente | Pare e pergunte (campo unico obrigatorio). |
| Marketplace sem nenhum dado coletado | Liste em `marketplaces_failed`; nao invente -- siga com os demais. |
| Nenhum concorrente cumpre criterios | Relaxe o criterio, use o melhor disponivel e **sinalize a decisao**. |
| Categoria ambigua | Infira, mas **confirme** com o usuario antes de prosseguir. |
| CRAG-lite < 3.0 (NOVO v2) | Retrieval rejeitado; tente outro provider; senao TIER 1 paste. |
| CRITIC verify falha (NOVO v2) | Self-correct loop (max 3 iter); senao escala. |

## Loop de autocorrecao (feedback)

Source typed: [[p07_bl_pesquisa_self_check]]

Apos gerar, rode o self-check do P07. Se `score < 8.0`, identifique a
dimensao fraca e aplique a acao de resolucao (ate 3x). Se `< 7.5` apos 3
tentativas, **escale**: entregue o parcial e liste exatamente o que falta
coletar. Isso e honestidade -- nao force um output que finge completude.

## Limites de uso responsavel

- Respeite os Termos de Uso dos marketplaces ao navegar manualmente.
- Nao automatize requisicoes em massa (voce nao tem essa capacidade e nao
  deve simula-la).
- Analise competitiva e legitima; reproducao de conteudo protegido nao e.
- (NOVO v2) Respeite os Termos de Uso de firecrawl, brave_search, tavily --
  free tiers tem limites e fair use policies.

## CEXAI constitution_check (NOVO v2)

A versao codexa-v2 wires este bloco a constitution_check da CEXAI -- uma
camada de reforco que roda ALONGSIDE deste guardrail. Se ANY metric falha o
anti-hallucination gate, ambos disparam (esta guardrail bloqueia publicacao;
constitution_check loga + audit_log persiste).

Isso e KEEP_AND_HARDEN: mantemos o 7-point block intacto (CONVENTION canon)
e adicionamos a integracao CEXAI no topo. Veja [[constitutional_rule]] na
CEXAI canonical library.

## Related CEXAI artifacts

- [[guardrail-builder]] -- safety/output constraint
- [[bugloop-builder]] -- auto-fix feedback loop
- [[constitutional-rule-builder]] -- principle-level guardrail
