---
agent: anuncio
pillar: P08
pillar_name: architecture
lang: pt-BR
source: api/v1/anuncios.py (stream pipeline V5, 5 stages); api/core/anuncio_synthesizer.py (cadeia sequencial F1-F5); api/core/anuncio_validator.py (quality 5D); records/pool/workflows/fat/FAT_ADW_ANUNCIO_V2.md (teaching, marketplace rules)
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: workflow
cexai_typed_artifacts:
  - cexai/workflow_anuncio_v5_pipeline.md
  - cexai/diagram_anuncio_pipeline_v5.md
  - cexai/decision_record_v5_supersedes_fat.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P08 -- Arquitetura do Pipeline (PRODUÇÃO V5 -- fonte primária)

Como o agente raciocina de ponta a ponta. Esta é a arquitetura de **produção V5** (o que a producao efetivamente roda), não o FAT legado. O bundle replica a **lógica**; a infra (multi-LLM, scraping, ERP) degrada -- ver P04.

> **Camada CEXAI:** workflow canônico em [[cexai/workflow_anuncio_v5_pipeline]] (5 estágios + cadeia sequencial + revision loop). Diagrama mermaid em [[cexai/diagram_anuncio_pipeline_v5]]. ADR justificando V5 sobre FAT em [[cexai/decision_record_v5_supersedes_fat]].

## Pipeline de produção (5 estágios SSE)

```
INPUT
  |
  v
[1] input_validation     --> confiança do input (0-1) + campos faltantes + ação
  |
  v
[2] research_enrichment  --> funde handoff de pesquisa; PRODUTO vence conflito
  |
  v
[3] generation           --> CADEIA SEQUENCIAL (sub-pipeline abaixo)
  |
  v
[4] quality_validation   --gate>=8.0--> rubrica 5D + auto-retry (máx. 2)
  |
  v
[5] erp_formatting       --> SKU/EAN/NCM/peso/dims (só dados reais) + BaseLinker
  |
  v
OUTPUT (content + quality_5d + erp + status APROVADO/REVISAR)
```

## Estágio 3 (generation) -- cadeia sequencial (o coração do agente)
Cada bloco consome a saída do anterior (coerência por construção). System instruction zero-fabricação é compartilhada em todos os blocos:

```
titles  ->  keywords  ->  bullets  ->  description  ->  faqs
(3, 58-60) (2x115-120)  (10, 250-299)  (>=5000 ML)    (5-7)
```

Pós-processo (sem LLM): extrai `technical_specs` (só de erp_fields/pesquisa), monta `html_description`, aplica **compliance ANVISA** (substituição de termos médicos) em TODOS os campos.

## Lógica de decisão por estágio

1. **input_validation** -- calcula confiança ponderada (product_name 0.20, category 0.10, head_terms 0.15, features 0.15, pain_points 0.10, gaps 0.10, specs 0.10...). Confiança baixa -> pergunte o que mais eleva qualidade ou marque `[PREENCHER]`.

2. **research_enrichment** -- extrai head_terms, longtails, gaps, complaints/praises, positioning, `suggested_price` (pricing_intelligence.sweet_spot). **Detecção de mismatch:** se product_name não tem overlap com head_terms, sinalize. **PRODUTO tem hierarquia máxima** -- em conflito, o produto vence a pesquisa.

3. **generation** -- ramifica limites pelo marketplace (`MARKETPLACE_SPECS`); gera a cadeia sequencial. Specs técnicas: usa se presentes no input/pesquisa, **OMITE se ausentes** (nunca inventa).

4. **quality_validation** -- roda 5D (titulo/keywords/descricao/bullets/factual). Retry dispara se qualquer dimensão falhar (não só overall). Escalada de temperatura/modelo por tentativa.

5. **erp_formatting** -- autopreenche SKU (de categoria+timestamp), EAN-13 (com dígito verificador), NCM (mapa por categoria) APENAS como sugestão editável; peso/dimensões fornecidos pelo usuário > scraped > default. Campos não confirmados ficam marcados para revisão.

## Estado entre estágios
A pesquisa (estágio 2) alimenta títulos, keywords, bullets e descrição. Keywords feed bullets+descrição; bullets feed descrição+FAQs. A dimensão **factual** garante que nada além do input/pesquisa entre no conteúdo. Estado mutável em [[cexai/working_memory_chain_state]].

## Tratamento de falha
- Circuit breaker: timeout global de 180s na geração; cada bloco tem timeout próprio (titles 45s, keywords 30s, bullets 45s, desc 60s, faqs 30s).
- Gate: se < 8.0 ou dimensão falha, retry da seção (máx. 2) com `ISSUE_TO_FIX` injetado (ver P07).
- `on_failure: partial_output` -- entregue o melhor, marcado REVISAR.
- No GPT standalone você é o único modelo; a "escalada" é mais esforço/precisão por retry.

## Equivalência FAT legado (teaching) -> V5 (produção)
| FAT legado | V5 produção | Diferença chave |
|------------|-------------|------------------|
| research_product | input_validation + research_enrichment | confiança + handoff |
| generate_title | generation.titles | -- |
| generate_description (StoryBrand 7-seções) | generation.bullets + description (6 folds) + faqs | V5 usa folds mobile-first, não 7 rótulos StoryBrand; bullets 250-299 |
| seo_optimize | generation.keywords | < 60 chars/termo, overlap <= 15% |
| marketplace_format + 5D (clarity/persuasion/...) | quality_validation (titulo/keywords/descricao/bullets/factual) + erp_formatting | 5D estrutural+factual; ERP real |

Decisão arquitetural documentada em [[cexai/decision_record_v5_supersedes_fat]].

## Related CEXAI artifacts

- [[workflow-builder]] -- stage-based execution graph
