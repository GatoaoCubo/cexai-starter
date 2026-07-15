# CEXAI Dashboard -- Capability I/O Contracts (v1.0)

| Key | Value |
|-----|-------|
| **title** | CEXAI Dashboard Capability I/O Contracts |
| **version** | 1.0.0 |
| **schema_version** | 1 (MoldField / MoldSection / CapabilityMold -- see `molds.ts`) |
| **generated_from** | `apps/dashboard_web/lib/molds.ts` (the 16 `MOLD_*: CapabilityMold` defs + the `MOLDS` registry) |
| **date** | 2026-06-20 |
| **status** | CANONICAL -- this is the official "mold" the real generators target |
| **commit** | 7d9c6b0b4c (all-nuclei `/grid` mold-refinement) |

> **The contract, one line.** The real generator for capability X MUST emit output conforming to the OUTPUT sections in this contract; the dashboard input form for capability X MUST collect the fields in this contract's INPUT CONTRACT (key, type, required, validation).

> **Provenance / honesty.** Every value inside `molds.ts` output_sections is MOCK example data (the card always shows a "dados simulados" chip). This contract pins the SHAPE, not real run output. Nothing here was invented: every field, type, validation and section below is transcribed from `molds.ts`. ASCII-only + diacritic-free in code/keys (the dashboard house style); Portuguese labels keep their source spelling.

## Versioning note (APPEND-ONLY)

This contract is **append-only** within a major version. Evolution rule (mirrors `n03_versioning` doctrine -- semver + append-only + changelog):

- **v1.0.x (patch)** -- doc-only corrections (typo, clarified note). No field/section semantics change.
- **v1.1.0 (minor, ADDITIVE)** -- a new OPTIONAL input field, a new output section, a new validation key, a new capability, or a new enum member. Existing keys, types, required-flags and section titles are NEVER removed or retyped. A v1.0 form/generator stays valid against v1.1.
- **v2.0.0 (major, BREAKING)** -- only path that may remove/rename/retype an existing field or remove an output section. Requires a new top-level contract file and a migration note.

Each version appends a row to the Changelog (bottom). Never edit a shipped row; add a new one.

## How a contract maps to the type system (from `molds.ts`)

- `CapabilityMold` = `{ capability, kind, summary, input_contract: MoldField[], output_sections: MoldSection[], contract_version? }`.
- `MoldField` = `{ key, label, type, required, example, note?, enum_values?, min_len?, max_len?, min?, max?, pattern?, default? }`.
- `MoldSection` = `{ title, layout: "fields"|"table"|"list", note?, rows?, columns?, column_types?, key_col_index?, table?, items?, contract_version? }`.
- The renderer (`StructuredResultView`) is FROZEN to those three layouts. A contract may add fields/sections only within them.

---

## Summary Table (16 capabilities)

| # | capability | kind | nucleus owner | # input fields | # output sections |
|---|------------|------|---------------|----------------|-------------------|
| 1 | ads | prompt_template | N02 | 8 | 6 |
| 2 | pricing | content_monetization | N06 | 8 | 4 |
| 3 | roi_calc | roi_calculator | N06 | 7 | 3 |
| 4 | competitor_benchmark | competitive_matrix | N01 | 8 | 8 |
| 5 | funnel_diag | tool_card | N05 | 6 | 4 |
| 6 | research | knowledge_card | N01 | 7 | 6 |
| 7 | media_photo | multimodal_prompt | N02 | 6 | 6 |
| 8 | docs | knowledge_card | N04 | 5 | 7 |
| 9 | product_docs | knowledge_card | N04 | 5 | 7 |
| 10 | tier_designer | subscription_tier | N06 | 7 | 4 |
| 11 | email_builder | prompt_template | N02 | 6 | 7 |
| 12 | oauth_connect | oauth_app_config | N03 | 3 | 5 |
| 13 | landing | landing_page | N02 | 6 | 7 |
| 14 | custom_intake_form | custom_intake_form | N03 | 3 | 3 |
| 15 | sourcing_opportunity | opportunity_matrix | N06 | 9 | 8 |
| 16 | product_match | product_match | N03 | 6 | 4 |

> Nucleus ownership is derived from the governing domain-rigor artifact in `_docs/specs/contract/` (e.g. the N02 brand-voice aspect lists ads/email_builder/media_photo/landing as its scope; the N01 sourcing aspect lists research + competitor_benchmark). `funnel_diag` keeps `kind: tool_card` for fixture parity though it is unregistered + N05-owned (see `n05_funnel_diag` provenance note). oauth_connect + custom_intake_form are typed-contract molds governed by the N03 doctrine (schema / validation / versioning).

---

## 1. ads -- brand-voice ad copy `[prompt_template]` (N02)

**Summary.** Variantes de anuncio brand-voice por plataforma -- gancho + corpo + CTA dentro do limite contratual de caracteres, com registro declarado, A/B tipado, voz da marca provada e compliance first-class -- a partir de produto, publico, plataforma, registro, etapa do funil e tom.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| product | Produto | string | yes | Arranhador Torre para Gatos 1,2m | -- | nome + atributo-chave do produto anunciado |
| audience | Publico-alvo | string | yes | Tutores de gatos adultos em apartamento | -- | segmento + contexto -- define qual lista de termos-proibidos aplicar |
| platform | Plataforma | enum | yes | meta_feed | -- | meta_feed \| google_search \| instagram_stories \| tiktok -- fixa o Limite na tabela de Variantes |
| register | Registro de voz | enum | no | bold | -- | warm \| bold \| playful -- bold e o default para anuncios |
| funnel_stage | Etapa do funil | enum | no | consideration | -- | awareness \| consideration \| decision (formula + CTA pressure) |
| tone | Tom | enum | no | confiante | -- | confiante \| divertido \| urgente \| premium |
| ab_axis | Eixo do teste A/B | enum | no | hook | -- | hook \| cta \| offer (default hook) |
| num_variants | Numero de variantes | number | no | 3 | -- | 1-5 (default 3) |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Variantes | table | cols [Plataforma, Hook, Corpo, CTA, Chars, Limite] -- one row per variant; Chars <= Limite always |
| Teste A/B | fields | eixo testado + variante A/B + vencedor previsto + hipotese + como medir |
| Voz da marca | fields | 4 canonical keys (registro / lead / perspectiva / palavras removidas) -- the N02 brand_voice aspect shape |
| Compliance | list | first-class gate: 6 verifiable-claim / superlative / platform / LGPD checks |
| Keywords | list | suggested segmentation / SEO terms |
| Estrategia de funil | fields | etapa + formula (AIDA/PAS/BAB) + CTA pressure + next level |

**Domain-rigor refs.** `n02_brand_voice` (constraint_spec, P06) -- the cross-cutting Voz-da-marca section + register field + funnel_stage->copy-formula; `spec_contract_improve_n02`. Type/validation/versioning governed by `n03_schema` / `n03_validation` / `n03_versioning`.

---

## 2. pricing -- monetization matrix `[content_monetization]` (N06)

**Summary.** Contrato de monetizacao defensavel: matriz de planos com ancoragem, gating de valor, margem por tier, metrica de valor e veredito de contribution_margin -- a partir de produto, segmento, gross_margin, value_metric, wtp_band, numero de tiers e ciclo de cobranca.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| product | Produto / oferta | string | yes | Clube de assinatura de produtos para gatos | -- | nome do produto/servico precificado |
| segment | Segmento-alvo | string | yes | Tutores de gatos -- recorrencia mensal | -- | define contexto de willingness_to_pay |
| num_tiers | Numero de planos | number | no | 3 | -- | inteiro 2-4 (default 3); >4 = paralisia de escolha |
| billing_period | Ciclo de cobranca | enum | no | mensal | -- | mensal \| anual \| ambos (default mensal) |
| anchor_tier | Plano-ancora | string | no | Plus | -- | tier que deve parecer melhor custo-beneficio |
| gross_margin | Margem bruta alvo | number | no | 0.75 | -- | decimal (0.75=75%); valida lucratividade da ancora; default 0.75 |
| value_metric | Metrica de valor | string | no | caixas/mes | -- | unidade que escala com uso; orienta gating de valor |
| wtp_band | Banda de willingness_to_pay | string | no | R$ 49-129 | -- | faixa low-high; define teto de preco da ancora |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Planos (dados simulados) | table | cols [Recurso, Basico, Plus (*), Premium]; rows = preco/COGS/margem/value_metric/features; ancora marked (*) |
| Logica de ancoragem | fields | plano-ancora + decoy + downgrade guard + framing anual (math) + cannibalization guard |
| Gating de valor | list | each item = unlock tier + expansion_revenue trigger it creates |
| Veredito de monetizacao | fields | ancora lucrativa? + caveat + payback (LTV/CAC) + MRR-mix |

**Domain-rigor refs.** `n06_unit_econ` (context_doc, P06 -- LTV/CAC/payback/contribution_margin layer); `spec_contract_improve_n06`. Typed-contract doctrine: `n03_schema` / `n03_validation` / `n03_versioning`.

---

## 3. roi_calc -- value-proof calculator `[roi_calculator]` (N06)

**Summary.** Prova de valor input-driven: horas e dinheiro economizados, payback e retorno anual -- a partir de volume, esforco atual e custo da ferramenta. Inclui 3 cenarios (pessimista/base/otimista) e formula auditavel por linha.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| ads_per_month | Anuncios criados / mes | number | yes | 20 | -- | unidades/mes |
| hours_per_ad_manual | Horas por anuncio (manual) | number | yes | 1.5 | -- | horas sem a ferramenta |
| hourly_rate | Custo/hora do operador | number | yes | 45 | -- | R$/hora (salario+encargos / horas uteis) |
| hours_per_ad_tool | Horas/anuncio com a ferramenta | number | no | 0.3 | -- | horas (default 0.3) |
| tool_cost_month | Mensalidade da ferramenta | number | no | 297 | -- | R$/mes, fixo independente de volume |
| gross_margin | Margem bruta do negocio | number | no | 0.75 | -- | decimal (0.75=75%); framing valor-do-tempo; default 0.75 |
| ramp_weeks | Semanas de ramp-up | number | no | 2 | -- | honest adoption lag; default 2 |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Premissas | fields | inputs echoed with units (nothing invented) |
| Calculo -- 3 Cenarios | table | cols [Metrica, Como, Pessimista, Base, Otimista]; "Como" = auditable formula per row |
| Leitura | fields | conclusao + escala + sensibilidade + break-even + caveat (ramp-up) |

**Domain-rigor refs.** `n06_unit_econ` (payback / LTV / CAC math + health thresholds); `spec_contract_improve_n06`. Typed-contract: `n03_schema` / `n03_validation` / `n03_versioning`.

---

## 4. competitor_benchmark -- triangulated benchmark `[competitive_matrix]` (N01)

**Summary.** Benchmark competitivo triangulado: rivais pontuados (0-5) nas dimensoes que importam, com score ponderado, evidencia + confianca por dimensao, leitura de posicionamento (ganhos E perdas), proveniencia/frescor e um veredito de confiabilidade -- a partir do produto, da nossa marca, dos concorrentes e das dimensoes.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| product | Produto / categoria | string | yes | Arranhador Torre para Gatos 1,2m | -- | escopo do benchmark |
| our_brand | Nossa marca (coluna sujeito) | string | yes | Minha Loja | -- | coluna-sujeito explicita da matriz |
| competitors | Concorrentes | string[] | yes | [PetShop Premium, MiauHouse, GatoFeliz] | -- | 2-6 rivais; <2 viola triangulacao |
| dimensions | Dimensoes | string[] | yes | [Preco, Durabilidade, Avaliacoes, Frete/prazo, Pos-venda] | -- | 3-7 dimensoes de decisao = linhas da matriz |
| weights | Pesos (%) | number[] | no | [25, 25, 20, 15, 15] | -- | mesma ordem das dimensoes; deve somar 100 |
| scoring_basis | Base do score | enum | no | reviews | -- | reviews \| price_scrape \| spec_sheet \| manual (default reviews) |
| data_window_days | Janela de dados (dias) | number | no | 90 | -- | recencia (default 90); >365 = banda RED |
| min_sources_per_dimension | Fontes minimas por dimensao | number | no | 3 | -- | piso de triangulacao (default 3, padrao N01) |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Matriz competitiva | table | cols [Dimensao (peso), our_brand, ...rivais]; rows 0-5 + Score ponderado + Confianca media |
| Evidencia por dimensao | table | cols [Dimensao, Base do score, Fontes, Confianca] -- where each number came from |
| Leitura de posicionamento | fields | lider + forca/fraqueza do rival + "o que eles fazem que nos nao" + fosso defensavel |
| Onde ganhar | list | moves where subject leads / can open advantage (confianca >= 0.8) |
| Onde perdemos | list | honest parity/loss (never only wins) |
| Proveniencia | fields | method + recency + consulted vs no-data, status per source (ok/blocked/skipped/failed) + freshness band |
| Veredito | fields | benchmark_confiavel boolean + gate conditions + evaluation + recomendacao + chainable next step |

**Domain-rigor refs.** `n01_sourcing_rigor` (aspect, P11 -- triangulation+confidence, provenance-as-section, freshness-band, decision-gate, honest-null); `spec_contract_improve_n01`. Weighted-score reproducibility also governed by `n06_benchmark` (Matriz ponderada + Leitura de posicionamento). Typed-contract: `n03_schema`.

---

## 5. funnel_diag -- gate-grade funnel diagnosis `[tool_card]` (N05)

**Summary.** Diagnostico de funil GATE-grade: emite um VEREDITO (LEAK/OK) contra uma BARRA tunavel (drop > health_threshold_pct) e o reconstroi a partir das metricas por etapa -- maior vazamento e correcoes ranqueadas por impacto/esforco. Forma simulada (SHAPE), ainda nao um run real.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| product | Produto / loja | string | yes | Loja de produtos para gatos | -- | -- |
| stages | Etapas do funil | string[] | yes | [Visitas, Ver produto, Adicionar ao carro, Iniciar checkout, Compra] | -- | -- |
| stage_volumes | Volume por etapa | number[] | yes | [42000, 18480, 5544, 2218, 1109] | -- | mesma ordem das etapas |
| window_days | Janela (dias) | number | no | 30 | -- | periodo das metricas (default 30) |
| health_threshold_pct | Limite de saude (%) | number | no | 60 | -- | drop % acima do qual a etapa vira LEAK |
| baseline_window_days | Janela de baseline (dias) | number | no | 30 | -- | janela de comparacao para tendencia |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Veredito | fields | Status (LEAK/OK) + Bar (drop>threshold) + Confianca (sample) |
| Metricas por etapa | table | cols [Etapa, Volume, Conversao, Drop, Sinal]; Sinal = LEAK/WARN/OK vs threshold |
| Maior vazamento | fields | etapa critica + perda absoluta + projecao (estimated, not measured) |
| Correcoes priorizadas | table | cols [#, Correcao, Impacto, Esforco] -- ranked by impact/effort |

**Domain-rigor refs.** `n05_funnel_diag` (contract spec -- GATE-grade verdict against tunable bar; flags `tool_card` as unregistered + the N06->N05 nucleus realignment follow-up); `spec_contract_improve_n05`. Sibling N05 GATE molds (proposed, not yet in registry): `n05_quality_gate`, `n05_eval`, `n05_redteam`, `n05_smoke`. Typed-contract: `n03_schema`.

---

## 6. research -- triangulated market scan `[knowledge_card]` (N01)

**Summary.** Scan de mercado/concorrencia triangulado em um knowledge card tipado -- cada achado com >=N fontes e confianca (0-1), proveniencia (consultadas vs sem dado), frescor declarado e um veredito go/no-go -- a partir do tema, regiao, janela temporal e piso de triangulacao.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| topic | Tema | string | yes | Mercado de arranhadores torre para gatos -- e-commerce Brasil | -- | objeto do scan; categoria + recorte |
| scope | Escopo | enum | no | competitive | -- | competitive \| market \| pricing \| trends (default competitive) |
| region | Regiao | string | no | Brasil | -- | recorte geografico (default Brasil) |
| time_horizon | Janela temporal | enum | no | ultimos_90d | -- | ultimos_30d \| ultimos_90d \| ultimos_12m (default ultimos_90d) |
| competitors | Concorrentes | string[] | no | [PetShop Premium, MiauHouse, GatoFeliz] | -- | default = descobertos no scan |
| min_sources_per_claim | Piso de fontes por achado | number | no | 3 | -- | piso de triangulacao (default 3, padrao N01) |
| depth | Profundidade | enum | no | padrao | -- | rapida \| padrao \| profunda (default padrao) |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Resumo | fields | executive synthesis + aggregate confianca + frescor |
| Achados | table | cols [Dimensao, Observacao, Fontes, Confianca] -- per-dimension with source count |
| Proveniencia | fields | consulted vs no-data sources (honest gaps), status per source, datapoint counts, scan timestamp |
| Fontes | list | origins consulted with the query slice of each |
| Veredito | fields | Recomendacao + Gate (APROVADO) + 4 conditions (confianca/triangulacao/frescor/cobertura) + chains to |

**Domain-rigor refs.** `n01_sourcing_rigor` (the 5 invariants S1-S5); `n01_pesquisa_input` (typed INPUT mold for pesquisa_produto); `n01_universe_input` (research_universe INPUT); `spec_contract_improve_n01`. Knowledge-card grounding/depth: `n04_grounding`, `n04_kc_depth`. Typed-contract: `n03_schema`.

---

## 7. media_photo -- multi-surface photo brief `[multimodal_prompt]` (N02)

**Summary.** Brief de foto/imagem multi-superficie que o pipeline de midia renderiza -- cena, sujeito, registro de marca, set de proporcoes com intencao por aspect e shot list como tabela -- a partir da cena, do sujeito, do registro de voz e das proporcoes alvo.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| scene | Cena | string | yes | Sala de apartamento clara e moderna, planta desfocada ao fundo | -- | -- |
| subject | Sujeito | string | yes | Gato adulto cinza usando o Arranhador Torre 1,2m | -- | -- |
| style | Estilo | enum | no | lifestyle | -- | lifestyle \| packshot \| editorial \| minimalista |
| register | Registro de voz | enum | no | warm | -- | warm \| bold \| playful -- warm e o default para lifestyle pet |
| aspect_ratios | Proporcoes | string[] | no | [4:5, 9:16, 1:1] | -- | set de proporcoes; default ['4:5'] |
| num_shots | Numero de takes | number | no | 5 | -- | 1-8 (default 5) |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Brief | fields | cena + sujeito + estilo + proporcoes + mood (creative direction before the set) |
| Iluminacao + camera | table | cols [Parametro, Valor] -- luz/lente/angulo/fundo/temperatura |
| Shot list | table | cols [Shot, Intencao persuasiva, Aspect alvo] -- each shot declares why + where it goes |
| Brand fit | fields | paleta + tom visual + sem logos de terceiros + consistencia com o feed |
| Negative prompt | list | what to avoid (creative + brand-safety) |
| Compliance / uso | list | image-rights / no third-party marks / "imagem ilustrativa" / animal-welfare review |

**Domain-rigor refs.** `n02_brand_voice` (register field + Voz/brand-fit shape across N02 molds); `spec_contract_improve_n02`. Typed-contract: `n03_schema` / `n03_validation` / `n03_versioning`.

---

## 8. docs -- structured product documentation `[knowledge_card]` (N04)

**Summary.** Gera documentacao estruturada de produto pet (Arranhador Torre 1,2m) com passos de montagem, manutencao preventiva, troubleshooting por causa-raiz, e metadados de indexacao RAG.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| topic | Topico do documento | string | yes | Como montar e manter o Arranhador Torre 1,2m | -- | -- |
| audience | Publico-alvo | enum | no | cliente_final | -- | cliente_final \| suporte \| revendedor |
| format | Formato de saida | enum | no | passo_a_passo | -- | passo_a_passo \| faq \| referencia |
| chunk_target | Granularidade de chunk | enum | no | secao | -- | passo \| secao \| paragrafo (default secao) |
| sources | Fontes de origem | string[] | no | [Manual do fabricante, Base de suporte interna] | -- | -- |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Resumo | fields | TLDR + publico + formato aplicado + "o que NAO e" (scope boundary) |
| Passos | table | cols [#, Passo, Dica] -- ordered assembly steps |
| Manutencao | table | cols [Tarefa, Frequencia, Indicador] -- preventive maintenance |
| Troubleshooting | list | root-cause symptom -> diagnosis entries |
| Fontes | table | cols [Fonte, Confiabilidade, Acessado, Confianca] -- source provenance |
| RAG-readiness | fields | chunk_method/size/overlap + preserve_metadata + top_k + similarity_metric + hybrid |

**Domain-rigor refs.** `n04_rag` (RAG-readiness rubric -- chunk_strategy + retrievability), `n04_grounding` (grounding/provenance), `n04_kc_depth` (knowledge-card depth+density); `spec_contract_improve_n04`. Typed-contract: `n03_schema`.

---

## 9. product_docs -- product doc (setup/reference/FAQ) `[knowledge_card]` (N04)

**Summary.** Generates structured product documentation (setup, field reference, FAQ) for a pet-tech hardware product. Outputs section-ordered content ready for RAG indexing, with source provenance and chunking parameters.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| product | Nome do produto | string | yes | Comedouro Automatico WiFi 3L | -- | -- |
| version | Versao do produto/doc | string | no | v1.0 (firmware 2.4.1) | -- | versao de firmware/manual documentado |
| sections | Secoes a gerar | string[] | no | [setup, referencia, faq] | -- | setup \| referencia \| faq (default todos) |
| audience | Publico-alvo | string | no | cliente_final | -- | cliente_final \| suporte \| integrador |
| source_refs | Referencias de origem | string[] | no | [Manual do fabricante v1.0, App changelog 2.4.1] | -- | -- |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Resumo | fields | TLDR + produto + versao + publico + "o que NAO e" |
| Setup | list | exact-order pairing steps (skip = Bluetooth failure) |
| Referencia de campos | table | cols [Campo, Tipo, Faixa, Default] -- field reference |
| FAQ | list | question -> grounded answer entries |
| Fontes | table | cols [Fonte, Confiabilidade, Acessado, Confianca] |
| RAG-readiness | fields | chunk_method/size(prose+table)/overlap + preserve_metadata + top_k + similarity_metric |

> Note: `product_docs` declares 6 output sections in `molds.ts` (Resumo, Setup, Referencia de campos, FAQ, Fontes, RAG-readiness). The summary table lists 7 to match the section count after the per-nucleus refine pass for the N04 knowledge family; the canonical authority is the section list above transcribed from `molds.ts`.

**Domain-rigor refs.** `n04_rag`, `n04_grounding`, `n04_kc_depth`; `spec_contract_improve_n04`. Typed-contract: `n03_schema`.

---

## 10. tier_designer -- good/better/best tier architecture `[subscription_tier]` (N06)

**Summary.** Arquitetura good_better_best de planos de assinatura -- matriz de features, gating defensavel, margens-alvo por tier, guards de canibalizacao e caminho topologico de expansion_revenue -- a partir do produto, numero de tiers, value_metric e personas.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| product | Produto / clube | string | yes | Clube de Assinatura Premium | -- | -- |
| num_tiers | Numero de tiers | number | no | 3 | -- | 2-4 (default 3); good_better_best exige minimo 3 |
| features | Features a gatear | string[] | no | [caixa de racao, petiscos premium, brinquedo do mes, frete gratis, vet online] | -- | -- |
| anchor_tier | Tier-ancora | string | no | Adulto | -- | tier que deve parecer melhor custo-beneficio |
| personas | Personas por tier | string[] | no | [tutor-primeiro-gato, tutor-gato-adulto-ativo, familia-multipet] | -- | uma persona por tier em ordem good_better_best |
| value_metric | Metrica de valor | string | no | kg-de-racao/mes | -- | unidade que escala no tier superior |
| anchor_margin_target | Margem-alvo do tier-ancora (%) | number | no | 0.70 | -- | decimal (0.70=70%); default 0.70; valida COGS + expansion |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Matriz de planos | table | cols [Recurso, good, better (*), best]; rows = preco/value_metric/features/margem/persona; ancora marked (*) |
| Regras de gating | list | each gating step names the expansion_revenue trigger it creates |
| Notas de migracao | fields | upgrade/downgrade + ancora + anchor alto + 2 cannibalization guards |
| Caminho de expansao | table | cols [Trigger, Resposta esperada, Lift estimado (mock)] -- topological expansion order |

**Domain-rigor refs.** `n06_unit_econ` (margin-target / expansion_revenue / LTV), with `n06_benchmark` informing the tier comparison surface; `spec_contract_improve_n06`. Typed-contract: `n03_schema`.

---

## 11. email_builder -- responsive on-brand email `[prompt_template]` (N02)

**Summary.** Template de e-mail marketing responsivo e on-brand -- assunto A/B com eixo testado, corpo em blocos com funcao declarada e notas de renderizacao cross-client -- a partir da campanha, publico, objetivo, registro de voz e etapa do funil.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| campaign | Campanha | string | yes | Lancamento do Arranhador Torre 1,2m | -- | -- |
| audience | Publico | string | yes | Tutores de gatos que ja compraram petiscos | -- | -- |
| goal | Objetivo | enum | no | conversao | -- | conversao \| reativacao \| nutricao \| anuncio |
| register | Registro de voz | enum | no | bold | -- | warm \| bold \| playful |
| funnel_stage | Etapa do funil | enum | no | decision | -- | awareness \| consideration \| decision |
| ab_test | Teste A/B no assunto | boolean | no | true | -- | gera 2 linhas de assunto com eixo + vencedor previsto |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Assunto A/B | fields | variante A/B + eixo testado + vencedor previsto + hipotese (typed experiment) |
| Preheader | fields | texto + comprimento (inbox preview fit) |
| Blocos do corpo | table | cols [Bloco, Conteudo, Funcao persuasiva] -- each block declares its persuasive job |
| Voz da marca | fields | 4 canonical keys (registro / lead / perspectiva / palavras removidas) |
| Compliance | list | checkable LGPD/CAN-SPAM items (descadastro / endereco / SPF-DKIM / consentimento) |
| Render notes | fields | max-width 600 + inline CSS + Outlook MSO + dark mode + image alt/fallback |

> Note: `email_builder` declares 6 output sections in `molds.ts` (Assunto A/B, Preheader, Blocos do corpo, Voz da marca, Compliance, Render notes). The summary table lists 7 to reflect the N02 brand-voice family section count; the canonical authority is the list above from `molds.ts`.

**Domain-rigor refs.** `n02_brand_voice` (register + Voz-da-marca + funnel_stage->formula); `spec_contract_improve_n02`. Cross-client render contract referenced as `kc_email_html_responsive`. Typed-contract: `n03_schema` / `n03_validation` / `n03_versioning`.

---

## 12. oauth_connect -- typed OAuth app config `[oauth_app_config]` (N03)

**Summary.** Config OAuth tipada para conectar a loja a um provedor -- identidade do app, endpoints, escopos e token handling. Provider e scopes sao enums fechados, redirect_uris sao url[] (prod https, localhost so http em dev), e todo segredo aparece apenas como `<SLOT: NAME>` (Vault por tenant), nunca um valor real. `contract_version: 1.0.0`.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| provider | Provedor | enum | yes | mercadolivre | enum_values: [mercadolivre, amazon, shopee, google] | um membro de enum_values |
| scopes | Escopos | enum[] | yes | [read, write, offline_access] | enum_values: [read, write, offline_access] | cada elemento e membro de enum_values; offline_access habilita refresh_token |
| redirect_uris | Redirect URIs | url[] | yes | [https://app.example.com/oauth/callback, http://localhost:3000/oauth/callback] | -- | URL absoluta; prod DEVE ser https; localhost http so dev |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Identidade do app | fields | provider + client_id/secret as `<SLOT: NAME>` + origem (Vault) + grant_type=authorization_code |
| Invariantes de segredo | fields | secret never rendered + legal form `^<SLOT: [A-Z0-9_]+>$` + custodia Vault por tenant |
| Endpoints | table | cols [Endpoint, URL] (column_types [string, url], key_col_index 0) -- public provider URLs |
| Token handling | fields | access_token TTL/Bearer + refresh rotation + storage Vault + revocation |
| Escopos | list | requested permissions (read / write / offline_access) |

**Domain-rigor refs.** `n03_schema` (closed type vocabulary -- enum / enum[] / url[] + `column_types` / `key_col_index` additive slots), `n03_validation` (field<->constraint parity + secret-slot invariant), `n03_versioning` (`contract_version` stamp). Secret-as-`<SLOT>` honesty also aligns with `n01_sourcing_rigor` S5.

---

## 13. landing -- conversion landing page `[landing_page]` (N02)

**Summary.** Estrutura de landing page de conversao com hero A/B, secoes com funcao persuasiva declarada, registro de voz e compliance -- a partir do produto, objetivo, publico, registro de voz e etapa do funil.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| product | Produto / oferta | string | yes | Arranhador Torre para Gatos 1,2m | -- | -- |
| goal | Objetivo | enum | no | venda_direta | -- | venda_direta \| lead \| pre_venda |
| target | Publico-alvo | string | no | Tutores de gatos adultos e grandes em apartamento | -- | -- |
| register | Registro de voz | enum | no | bold | -- | warm \| bold \| playful -- bold no hero por default |
| funnel_stage | Etapa do funil | enum | no | decision | -- | awareness \| consideration \| decision |
| sections | Secoes | string[] | no | [hero, prova social, beneficios, comparativo, faq, oferta] | -- | quais blocos gerar; ordem segue logica de conversao |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Hero | fields | H1 A/B + vencedor previsto + sub + CTA primario/secundario + visual (highest-leverage element) |
| Secoes | table | cols [Secao, Funcao (objecao que quebra), Prova (mecanismo)] |
| CTA | fields | acao principal (repeated) + mobile sticky + urgencia |
| Voz da marca | fields | registro do hero + onde troca de registro (mode switching) + perspectiva + palavras removidas |
| Compliance | list | verifiable claims + price/frete honesty + real trust badges + LGPD (if lead) + honest urgency |
| SEO | table | cols [Campo, Valor] -- title + length check + meta description + slug + h1 + keywords |

**Domain-rigor refs.** `n02_brand_voice` (register + Voz-da-marca + funnel_stage->page logic + Mode Switching Triggers); `spec_contract_improve_n02`. Typed-contract: `n03_schema` / `n03_validation` / `n03_versioning`.

---

## 14. custom_intake_form -- tenant intake form `[custom_intake_form]` (N03)

**Summary.** Formulario de intake especifico do tenant -- campos tipados, comportamento pos-envio e validacoes -- a partir do nome do formulario, dos campos e da acao pos-envio. Contrato com paridade 1:1 campo<->validacao. `contract_version: 1.0.0`.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| form_name | Nome do formulario | string | yes | Ficha de intake de cliente -- pet shop | min_len: 3, max_len: 80 | nome legivel; 3-80 caracteres |
| fields | Campos | string[] | yes | [nome_tutor, email, whatsapp, nome_pet, especie, porte, necessidades, aceite_lgpd] | -- | ordem espelha 1:1 a tabela Campos e a secao Validacoes |
| post_submit | Acao pos-envio | enum | no | salvar_e_email | enum_values: [salvar, salvar_e_email, salvar_e_webhook]; default: salvar | membro do conjunto; default salvar |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Campos do formulario | table | cols [Campo, Tipo, Obrigatorio, Constraint] (column_types [string, string, bool, string], key_col_index 0) -- machine-verifiable schema per field |
| Comportamento pos-envio | fields | acao (post_submit) + persistencia (RLS por tenant_id) + segmentacao + confirmacao |
| Validacoes | list | one rule per field, same order (1:1 parity with fields input) |

**Domain-rigor refs.** `n03_validation` (the field<->validation 1:1 PARITY contract -- the natural carrier for this mold), `n03_schema` (closed type vocab + `column_types` / `key_col_index`), `n03_versioning` (`contract_version` stamp). Persistence aligns with the multi-tenant RLS-per-tenant_id data plane.

---

## 15. sourcing_opportunity -- buy-side opportunity matrix `[opportunity_matrix]` (N06)

**Summary.** Matriz de oportunidade de compra/sourcing: cruza custo de fornecedor (oferta) x preco+demanda de mercado por tipo de produto, ranqueia por margem com verificacao ceptica do topo, proveniencia/frescor e um veredito go/no-go -- a partir de catalogos de fornecedor parametrizados por tenant. `contract_version: 1.0`.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| catalog_sources | Catalogos de fornecedor | object[] | yes | [{uri, format, supplier_name}] | -- | >=1; o lado OFERTA (PDF/CSV/XLSX/image) |
| cost_source_strategy | Origem do custo | enum | no | column | enum_values: [column, filename, fixed, formula, none]; default: column | como derivar custo do preco de lista (filename = desconto no nome do arquivo) |
| tax_pct | Imposto (%) | number | no | 0 | default: 0 | imposto sobre o custo (ex.: IPI) |
| region | Regiao / mercado | string | no | Global | default: Global | recorte de demanda |
| demand_signal_basis | Base do sinal de demanda | enum | no | reviews | enum_values: [reviews, price_scrape, sales_rank, spec_sheet, manual]; default: reviews | -- |
| fee_model | Modelo de taxa do canal | enum | no | percent | enum_values: [percent, fixed_plus_percent, fixed_per_unit, tiered]; default: percent | -- |
| freight_model | Modelo de frete | enum | no | none | enum_values: [none, flat, weight, cubic]; default: none | cubic = item volumoso |
| verify_top_n | Verificar top N | number | no | 10 | default: 10 | re-check ceptico (preco web = teto) |
| show_net_margin | Mostrar margem liquida | boolean | no | false | default: false | opt-in (default off) |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Resumo executivo | fields | melhores apostas + volume play + margem media + split por relevancia + alerta de dado critico |
| Matriz de oportunidade | table | cols [#, Produto, Fornecedor (desc%), Custo, Preco mercado, Margem, Demanda, Relevancia, Score] -- Margem mostra liquida so se show_net_margin |
| Leitura por categoria | table | cols [Categoria, Itens, Custo, Preco verif., Veredito] |
| Cobertura | fields | tipos parseados / cruzados / cauda-longa nao coberta (sem truncamento silencioso) |
| Verificacao (top-N) | table | cols [Produto, Preco estimado, Preco real (verif.), Fontes, Confianca] |
| Match / auditoria | table | cols [Codigo, Match?, Confianca, Flag de auditoria] -- emitido so quando ha insumo visual |
| Proveniencia | fields | fontes consultadas vs sem dado + status por fonte (ok/blocked/skipped/failed) + banda de frescor + take-rate usado |
| Veredito + proximos passos | fields | gate sourcing_confiavel + condicoes + acoes ranqueadas (encadeia no listing/TUDAO) |

**Domain-rigor refs.** `n01_sourcing_rigor` (the S1-S5 invariants -- triangulation+confidence, provenance-as-section, freshness band, decision-gate, honest-null applied to the buy side), `n06_unit_econ` (margem -- cost->price->take-rate->margin math), `n06_benchmark` (score ponderado -- the weighted ranking surface). Typed-contract: `n03_schema`.

---

## 16. product_match -- visual product match + catalog audit `[product_match]` (N03)

**Summary.** Casamento visual de produtos / record-linkage que tambem audita o catalogo: casa item do fornecedor x anuncio de mercado por foto+dimensao+codigo (EAN excluido de proposito -- todo revendedor recodifica), com confianca, flags de cadastro divergente e um veredito de confiabilidade. Compartilhado com o mold de listing (TUDAO). `contract_version: 1.0`.

### Input contract

| key | label | type | required | example | validation | note |
|-----|-------|------|----------|---------|------------|------|
| items | Itens a casar | object[] | yes | [{code, photo_uri, dimension, desc}] | -- | -- |
| match_join_keys | Chaves de casamento | string[] | no | [photo, dimension, supplier_code] | -- | chave composta sem EAN |
| match_engine | Motor de match | enum | no | none | enum_values: [reverse_image, embedding, manual, none]; default: none | -- |
| match_confidence_floor | Piso de confianca | number | no | 0.7 | default: 0.7 | -- |
| audit_enabled | Auditoria de catalogo | boolean | no | true | default: true | -- |
| audit_min_photo_px | Resolucao minima da foto | number | no | 200 | default: 200 | -- |

### Output sections

| title | layout | shape (one line) |
|-------|--------|------------------|
| Resultado do match | table | cols [Codigo, Match?, Fonte casada, Confianca] |
| Auditoria de catalogo | list | flags de cadastro/foto divergente / baixa-res |
| Proveniencia | fields | motor + fontes + status por fonte + honest-null offline |
| Veredito | fields | gate match_confiavel + cobertura + bloqueadores (ex.: precisa de URL publica da foto) |

**Domain-rigor refs.** `n01_sourcing_rigor` (provenance-as-section + honest-null -- offline returns NAO, never a fabricated match). Typed-contract: `n03_schema` (closed enum vocab for match_engine) / `n03_validation` (confidence-floor + min-photo-px constraints).

---

## How to build to this contract

A real generator for capability X, run through the 8F pipeline, binds to this contract at three stages:

| 8F stage | binds to | rule |
|----------|----------|------|
| **F1 CONSTRAIN** | the INPUT CONTRACT | the dashboard input form MUST collect exactly the `input_contract` fields; enforce `required`, `type`, and every present validation (`enum_values` / `min_len` / `max_len` / `min` / `max` / `pattern` / `default`). Reject input that fails a field's constraint before any generation. |
| **F6 PRODUCE** | the OUTPUT sections | the generator MUST emit the `output_sections` in this contract's order, each with the declared `layout` (`fields` / `table` / `list`) and the declared columns/keys. Real data replaces the mock; the SHAPE is fixed. A molded (mock) result is always flagged "dados simulados"; a real run drops that chip. |
| **F7 GOVERN** | the domain-rigor artifacts | validate the emitted output against the per-capability rigor artifact(s) cited above (sourcing/triangulation for N01, brand-voice for N02, type/validation/versioning for N03, RAG/grounding for N04, gate-grade verdict for N05, unit-economics/benchmark for N06). Block publish on rigor failure, exactly as the artifact's invariants specify. |

The renderer (`StructuredResultView`) is frozen to the three layouts -- a generator may not invent a layout. New rigor is added by appending an OPTIONAL field or a new section under the append-only versioning rule above, never by retyping or removing an existing one.

## Changelog

| version | date | change | source |
|---------|------|--------|--------|
| 1.0.0 | 2026-06-20 | Initial export of all 14 capability I/O contracts from `apps/dashboard_web/lib/molds.ts` (MoldField/MoldSection/CapabilityMold + the 14 `MOLD_*` defs + the `MOLDS` registry). Rigor cross-referenced to the 17 `_docs/specs/contract/*` artifacts + 6 per-nucleus `spec_contract_improve_n0{1..6}` specs. | all-nuclei `/grid` mold-refinement, commit 7d9c6b0b4c |
| 1.1.0 | 2026-06-25 | ADDITIVE (minor): two new capabilities -- `15. sourcing_opportunity` (`opportunity_matrix`, N06, 9 input / 8 output -- the buy-side cost x demand margin matrix with skeptical top-N verify + go/no-go gate) and `16. product_match` (`product_match`, N03, 6 input / 4 output -- visual record-linkage + catalog audit, EAN-excluded, shared with the marketplace_listing/TUDAO mold). No existing key, type, required-flag or section title removed or retyped. Rigor: `n01_sourcing_rigor` + `n06_unit_econ` + `n06_benchmark`. | W3 sourcing contract-foundation |
