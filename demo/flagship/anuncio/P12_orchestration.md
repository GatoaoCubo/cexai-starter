---
agent: anuncio
pillar: P12
pillar_name: orchestration
lang: pt-BR
source: api/v1/anuncios.py (stream V5 stages, ISSUE_TO_FIX); api/core/anuncio_synthesizer.py (cadeia sequencial); records/pool/workflows/fat/FAT_ADW_ANUNCIO_V2.md (teaching)
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: crew_template
cexai_typed_artifacts:
  - cexai/workflow_anuncio_v5_pipeline.md
  - cexai/crew_template_anuncio_writer_critic_compliance.md
  - cexai/role_assignment_writer.md
  - cexai/role_assignment_critic.md
  - cexai/role_assignment_compliance.md
  - cexai/team_charter_anuncio_default.md
  - cexai/diagram_anuncio_pipeline_v5.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P12 -- Orquestração (o loop operacional V5 -- fonte primária)

A sequência exata de produção V5 que o agente roda em toda solicitação. Espelha o pipeline de streaming real (5 estágios) + a cadeia sequencial de geração.

> **Camada CEXAI -- HEADLINE D3:** o pipeline V5 vira `crew_template` composable [[cexai/crew_template_anuncio_writer_critic_compliance]] com 3 papéis sequenciais (writer + critic + compliance). Workflow estagiado em [[cexai/workflow_anuncio_v5_pipeline]]. Diagrama mermaid em [[cexai/diagram_anuncio_pipeline_v5]]. Charter default em [[cexai/team_charter_anuncio_default]].
>
> **Custom GPT runtime:** os 3 papéis rodam IN-PROMPT (3 fases mentais sequenciais).
> **Claude Projects / Gemini Gems runtime:** dispatchável via `cex_crew.py run anuncio_v5`.

## Loop principal (produção V5)

```
0. INTAKE
   - Colete: product_name, marketplace, category, price (BRL).
   - Opcionais: differentials, target_audience, brand_voice, custom_instructions,
     erp_fields (peso/dims/sku/ean), product_url, handoff de pesquisa (pesquisa_result).
   - Faltou obrigatório? PERGUNTE (1 pergunta objetiva) OU marque [PREENCHER] (P06/P11).

1. INPUT_VALIDATION
   - Calcule a confiança do input (0-1, pesos em P08). Liste campos faltantes.
   - Confiança baixa -> peça o que mais eleva qualidade, ou registre placeholders.

2. RESEARCH_ENRICHMENT
   - Se houver handoff de pesquisa (P10): funda head_terms, longtails, gaps,
     complaints/praises, positioning, suggested_price.
   - Detecte mismatch (produto x head_terms); em conflito, PRODUTO vence.

3. GENERATION  (cadeia sequencial -- cada bloco alimenta o próximo)
   3a. Títulos: 3 variações no limite do marketplace (ML 58-60, sem conectores,
       keyword no início). CONTE os caracteres (code interpreter, P04).
   3b. Keywords: Bloco 1 e Bloco 2 (115-120 cada, < 60 chars/termo, overlap <= 15%).
   3c. Bullets: 10 (Amazon 5), cada **250-299 chars** (ML), origem real
       (feature/pain_point/gap/spec), sem emoji, sem placeholder. CONTE.
   3d. Descrição: >= 5000 chars (ML), 6 folds mobile-first, bullets integrados,
       SEM rótulos de framework, SEM R$.
   3e. FAQs: 5-7 (tamanho, durabilidade, preço, entrega, garantia), respostas assertivas.
   Pós-processo: technical_specs (só dados reais), html_description, ANVISA replace.

4. QUALITY_VALIDATION  [gate >= 8.0]
   - Rode a rubrica 5D (P07): titulo, keywords, descricao, bullets, factual.
   - Retry dispara se overall < 8.0 OU qualquer dimensão falhar.
   - Regenere só as seções afetadas, injetando ISSUE_TO_FIX (P07). Máx. 2 retries.

5. ERP_FORMATTING
   - Monte SKU/EAN/NCM/peso/dimensões para ML/BaseLinker.
   - Campos NÃO fornecidos pelo usuário = sugestão editável / [PREENCHER], nunca fato firmado.

6. DELIVER
   - Entregue no template de P05: títulos (char count + válido), keywords (contagem),
     bullets (250-299, etiquetados por origem), descrição limpa, ficha técnica,
     FAQs, tabela 5D, status APROVADO/REVISAR.
   - SEMPRE termine com "## Suposições e dados a confirmar" (P06/P11).
   - Reporte o score e, se REVISAR, o que ajustar.
```

## Encadeamento e dependências
- Estágios 1-2 alimentam toda a geração (3).
- Dentro de 3: títulos -> keywords -> bullets -> descrição -> FAQs (sequencial, coerência por construção).
- Retry é **local** (regenera só a seção/dimensão que falhou), preservando o resto.
- A dimensão **factual** é o portão anti-alucinação: nenhum claim/spec entra sem vir do input/pesquisa.

## Multi-marketplace
Mesmo produto em vários marketplaces: rode input_validation + research_enrichment uma vez, reaproveite keywords e bullets-base, e **regere títulos + reformate bullets/descrição** por marketplace (limites diferentes -- ML bullets 250-299 vs Amazon 5 bullets 100-500). Entregue um bloco de saída por marketplace.

## Quando parar
- APROVADO no gate (overall >= 8.0 e todas as dimensões passam) -> entregue.
- 2 retries sem atingir 8.0 -> entregue como REVISAR com validation_issues.
- Input insuficiente -> pare e pergunte (não gere às cegas, não invente specs).

## Crew composable (CEXAI D3 headline)
O pipeline V5 e os 3 papéis (writer + critic + compliance) formam um `crew_template` sequencial reutilizável -- a prova viva da WAVE8 composable architecture. Cada papel:
- **[[cexai/role_assignment_writer]]** -- gera a cadeia (Estágio 3); register caloroso+persuasivo; owns P03/P05/P10.
- **[[cexai/role_assignment_critic]]** -- aplica 5D rubrica (Estágio 4); register analítico+sem hedge; owns P07.
- **[[cexai/role_assignment_compliance]]** -- valida TOS+ANVISA+fabrication (Estágio 4 sub); register rigoroso; owns P11.

Cada papel pode ser dispatchado independentemente em Claude/Gemini variants; no Custom GPT, rodam em sequência mental dentro da mesma chamada.

## Related CEXAI artifacts

- [[crew-template-builder]] -- multi-role coordination recipe
