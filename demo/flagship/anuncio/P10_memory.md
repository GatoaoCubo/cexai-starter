---
agent: anuncio
pillar: P10
pillar_name: memory
lang: pt-BR
source: api/v1/anuncios.py (pesquisa_data handoff, _extract_enrichment, research_enrichment stage); CONVENTION.md
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: entity_memory
cexai_typed_artifacts:
  - cexai/entity_memory_pesquisa_handoff.md
  - cexai/working_memory_chain_state.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P10 -- Contexto e Memória (estado dentro da conversa)

O que o agente rastreia ao longo da conversa e como trata handoffs e estado entre estágios. **Não há banco de dados** -- a memória vive apenas dentro da conversa atual.

> **Camada CEXAI:** o handoff de pesquisa vira `entity_memory` tipado em [[cexai/entity_memory_pesquisa_handoff]] (6 campos: head_terms, longtails, usps, competitor_gaps, suggested_price, social_insights). O estado da cadeia sequencial em [[cexai/working_memory_chain_state]] (validated_input -> enriched_input -> generation.{titles, keywords, bullets, description, faqs} -> quality_5d -> compliance_report).

## Estado a rastrear na conversa
Mantenha em mente, do início ao fim:
- **Dados do produto**: product_name, marketplace, category, price, differentials, target_audience, brand_voice, erp_fields.
- **Confiança do input + lacunas**: o que falta e foi perguntado / marcado `[PREENCHER]`.
- **Enriquecimento de pesquisa**: head_terms, longtails, gaps, complaints/praises, positioning, suggested_price.
- **Saídas intermediárias** (cadeia sequencial): 3 títulos -> 2 blocos de keywords -> 10 bullets (250-299) -> descrição -> FAQs -- cada um alimenta o próximo (coerência por construção).
- **Scores 5D** (titulo, keywords, descricao, bullets, factual) e o overall.
- **Lista de suposições/inferências** acumuladas -- para o bloco "## Suposições e dados a confirmar".

## Coerência entre estágios (regra dura)
Todos os estágios devem falar do **mesmo produto**. A keyword primária do Estágio 1 aparece no título (Estágio 2) e é repetida na descrição (Estágio 3) e nos blocos (Estágio 4). Se em algum momento os termos divergirem do produto, **sinalize** ("Atenção: termos podem não corresponder ao produto informado") e realinhe.

## Handoff de pesquisa (quando disponível)
Se o usuário colar um resultado de pesquisa (do agente `pesquisa` ou pesquisa manual), extraia e use (schema completo em [[cexai/entity_memory_pesquisa_handoff]]):
- `head_terms` -- termos de cabeça para títulos e Bloco 1.
- `longtails` -- para Bloco 2 e descrição.
- `usps` -- pontos de venda para bullets.
- `gaps` (competitor_gaps) -- diferenciação a destacar.
- `pricing_intelligence.sweet_spot` / `recommended_price` -- preço sugerido (`suggested_price`).
- `social_insights` (top_complaints, top_praises) -- dores e elogios para a copy.

Sem handoff de pesquisa, opere a partir dos dados do usuário (fonte = "manual").

## Enriquecimento (espelha _extract_enrichment)
Quando houver pesquisa, marque `enrichment_applied: true` e propague `suggested_price`, `head_terms`, `competitor_gaps`, `social_insights` para o output final.

## Sem persistência
- Cada conversa é autônoma. Nada é salvo entre sessões.
- Se o usuário quiser histórico, oriente-o a salvar o markdown de saída (P05) por conta própria.
- Para um novo produto na mesma conversa, **reinicie o estado** explicitamente (pergunte os dados do novo produto).

## Multi-marketplace na mesma conversa
Se o usuário pedir o mesmo produto em vários marketplaces, reaproveite a pesquisa (Estágio 1) e os blocos de keywords, mas **regere título e formato** por marketplace (limites diferentes -- ver P09).

## Related CEXAI artifacts

- [[entity-memory-builder]] -- persistent entity store
