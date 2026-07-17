---
agent: pesquisa
pillar: P05
pillar_name: output
lang: pt-BR
source: api/core/pesquisas_executor.py (RESEARCH_SYSTEM_PROMPT JSON schema)
fidelity: full
cexai_reference_kind: formatter + parser
cexai_source_of_truth: cexai/p05_fm_pesquisa_report.md + cexai/p06_if_handoff_to_anuncio.md
---

# P05 -- Contratos de Saida

O agente entrega DOIS artefatos: (A) um relatorio legivel em Markdown e
(B) o bloco JSON de handoff. Ambos no fim de toda pesquisa completa.

> Espelho CONVENTION-friendly de [[p05_fm_pesquisa_report]] (formatter) +
> [[p06_if_handoff_to_anuncio]] (parser/interface).

## REGRA DE ENTREGA -- sempre em bloco de codigo (OBRIGATORIO)

Todo entregavel final SAI dentro de bloco(s) de codigo markdown (cercados por
` ``` `), em **texto simples**, para o usuario **copiar e colar direto**.

- **Um bloco de codigo por unidade copiavel.** Em pesquisa: **um bloco por
  secao do relatorio** (Queries / Marketplace / Concorrentes / SEO /
  Gaps) -- **mais um bloco separado** para o JSON de handoff.
- Texto explicativo/conversa do agente fica **FORA** dos blocos; o
  conteudo-produto fica **DENTRO**.
- O bloco "## Suposicoes e dados a confirmar" pode ficar **FORA** do code
  block (e meta).
- NUNCA entregue o conteudo final so como markdown renderizado ou prosa solta.

## A) Relatorio (Markdown) -- formato fixo

```markdown
# RESEARCH NOTES: [NOME DO PRODUTO]

**Gerado em**: [DATA]
**Confidence**: [X.X]/10
**Queries usadas**: [N]

---

## 1. QUERIES GERADAS
### Head Terms ([N])
[lista -- sem acento]
### Longtails ([N])
[lista -- sem acento]
### Sinonimos ([N])
[lista -- sem acento]

---

## 2. ANALISE DE MARKETPLACE
### Mercado Livre
- Faixa de preco: R$ [X] - R$ [Y]
- Sweet spot: R$ [Z]
- Padroes de titulo: [lista]
### Shopee / Amazon BR / Magalu / Americanas
[mesma estrutura -- so os marketplaces pesquisados]

---

## 3. ANALISE DE CONCORRENTES
### Concorrente 1: [NOME] ([marketplace])
- Preco: R$ [X] | Reviews: [N] | Nota: [X.X] | Vendidos: [N] | Origem: [paste|browsing|firecrawl|brave|tavily|user]
- Forcas: [lista]
- Fraquezas: [lista]
- Gaps: [lista]
[repetir para 3-5 concorrentes. Todo numero traz a ORIGEM (P04). Dado ausente = `[A CONFIRMAR]`, nunca inventado.]

### Resumo de Benchmark
| Metrica | Min | Max | Media | Recomendado |
|---------|-----|-----|-------|-------------|
| Preco   | R$X | R$Y | R$Z   | R$W         |
| Reviews | N   | N   | N     | --          |

---

## 4. TAXONOMIA DE SEO
### Inbound -- alta intencao
[lista]
### Outbound -- midia paga
[lista]
### Negativas
[lista]
### Category paths
- ML: [caminho] | Shopee: [caminho] | Amazon: [caminho]

---

## 5. GAPS & OPORTUNIDADES
1. [Gap] -> [Oportunidade]
2. [Gap] -> [Oportunidade]
### Posicionamento recomendado
[2-3 frases]

---

## Suposicoes e dados a confirmar
[Liste TUDO que nao foi coletado e foi inferido, deixado como `[A CONFIRMAR]`,
ou marcado `estimado`. Inclua os `marketplaces_failed`. Se nada faltou, escreva
"Nenhuma -- todos os dados tem origem verificavel (paste/firecrawl/brave/tavily/user)."]

---

**Quality**: [X.X]/10  |  **Pronto para Anuncio**: [SIM/NAO]
```

## B) Bloco HANDOFF (JSON) -- contrato para o proximo agente

Os campos seguem o schema do backend (`RESEARCH_SYSTEM_PROMPT`). Nomes
exatos. Schema completo em [[p06_if_handoff_to_anuncio]].

```json
{
  "head_terms": ["..."],
  "longtails": ["..."],
  "synonyms": ["..."],
  "marketplace_data": {
    "mercado_livre": {}, "shopee": {}, "amazon_br": {},
    "magalu": {}, "americanas": {}
  },
  "price_analysis": { "min": 0, "max": 0, "avg": 0, "currency": "BRL" },
  "competitors": [
    { "name": "", "url": "", "marketplace": "", "price": 0, "reviews_count": 0, "rating": 0.0, "strengths": [], "weaknesses": [], "gaps": [] }
  ],
  "benchmark": {},
  "gaps": ["..."],
  "opportunities": ["..."],
  "seo_inbound": ["..."],
  "seo_outbound": ["..."],
  "negative_keywords": ["..."],
  "category_paths": {},
  "validation_score": 0.0,
  "mock": false,
  "marketplaces_failed": ["..."],
  "data_sources": { "<campo ou marketplace>": "paste|browsing|firecrawl|brave|tavily|user|estimado" }
}
```

> `mock` e SEMPRE `false`. `marketplaces_failed` lista marketplaces sem dado
> coletado. `data_sources` mapeia a ORIGEM de cada metrica (rastreabilidade,
> P04). Campos sem dado coletado: lista/objeto vazio -- nunca numero inventado.

### Mini-handoff para o agente de anuncio
```yaml
head_terms: [array]
longtails: [array]
synonyms: [array]
pain_points: [inferidos dos gaps]
desired_gains: [inferidos das oportunidades]
price_recommendation: R$ [X]
```

## Regras de output

1. Sempre os DOIS artefatos (Markdown + JSON) numa pesquisa completa, **cada
   unidade no seu code block** (regra de entrega no topo).
2. `validation_score`/Confidence sempre presente (0-10).
3. Campos sem dado coletado: deixe a lista/objeto vazio ou marque "estimado"
   -- nunca preencha com numero inventado.
4. Queries SEM acento; texto do relatorio COM acento (PT-BR).
5. Conteudo-produto DENTRO de bloco de codigo; conversa e o bloco
   "Suposicoes" FORA.
6. NOVO em v2: campo `data_sources` agora aceita os 3 action providers
   (`firecrawl`, `brave`, `tavily`) alem dos legados (paste/browsing/user/estimado).

## Related CEXAI artifacts

- [[formatter-builder]] -- output formatter
- [[parser-builder]] -- structured-output parser
