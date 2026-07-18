---
kind: instruction
id: bld_instruction_research_pipeline
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para artefatos de research pipeline
pattern: pipeline de 3 fases (pesquisar -> compor -> validar)
quality: null
title: "Instruções: Pipeline de Pesquisa"
version: "1.0.0"
author: n03_builder
tags: [research_pipeline, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos para a construção de pipelines de pesquisa, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de pipeline de pesquisa"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
keywords: [research pipeline construction, instruction research pipeline, research_pipeline, builder, examples, write pipeline, write source catalog, write config schema, write multi, model routing]
density_score: 0.90
related:
  - research-pipeline-builder
---
# Instruções: Como Produzir um research_pipeline

## Fase 1: PESQUISAR
1. Identifique o negócio-alvo: nicho, país, idioma, panorama de marketplaces
2. Catalogue as fontes de dados disponíveis por categoria (inbound/outbound/search/trends/RAG)
3. Para cada fonte: documente API, autenticação, rate limit, custo, qualidade dos dados
4. Defina perspectivas STORM relevantes para o nicho (5 ângulos de especialista)
5. Escolha o roteamento multi-modelo: qual modelo cuida de qual etapa/domínio
6. Defina restrições de orçamento: tetos mensais, limites por pesquisa, pools de créditos
7. Defina os requisitos de output: formatos (HTML/PPTX/JSON), idioma, estilo de template
8. Verifique artefatos research_pipeline existentes para evitar sobreposição de config

## Fase 2: COMPOR
1. Leia bld_schema_research_pipeline.md -- fonte da verdade para os campos de config
2. Leia bld_output_template_research_pipeline.md -- estrutura do template
3. Preencha o frontmatter: id, kind, pillar, title, version, quality: null
4. Escreva a seção Pipeline: 7 etapas com detalhe por etapa:
   - **Etapa 1 INTENT**: classifica domínio, verbo, complexidade → rota
   - **Etapa 2 PLAN (STORM)**: 5 perspectivas × 5-7 subperguntas cada
   - **Etapa 3 RETRIEVE (CRAG)**: busca paralela nas fontes, gate de qualidade por resultado
   - **Etapa 4 RESOLVE**: dedup de entidades cross-fonte (similaridade de EAN/GTIN/título)
   - **Etapa 5 SCORE**: pontuação em 7 dimensões Gartner por listagem/resultado
   - **Etapa 6 SYNTHESIZE (GoT)**: merge Graph-of-Thoughts via modelos específicos do domínio
   - **Etapa 7 VERIFY (CRITIC)**: modelo de raciocínio verifica e corrige (max 3 iterações)
5. Escreva o Catálogo de Fontes: todas as fontes agrupadas por categoria
6. Escreva o Schema de Config: todos os campos variáveis agrupados por seção
7. Escreva o Roteamento Multi-Modelo: modelo por etapa/domínio com justificativa de custo
8. Escreva os Controles de Orçamento: tetos mensais, limites por pesquisa
9. Escreva os Gates de Qualidade: limiares de CRAG, iterações de CRITIC, mínimo final
10. Garanta zero nomes de país/marketplace hardcoded -- TUDO via config

## Fase 3: VALIDAR
1. Verifique se as 7 etapas do pipeline estão documentadas com entrada/saída/modelo
2. Verifique se o catálogo de fontes cobre 4 categorias (inbound, outbound, search, trends)
3. Verifique que não há chaves de API em texto plano -- apenas referências a ENV_VAR
4. Verifique se as perspectivas STORM são personalizáveis (não hardcoded)
5. Verifique se os controles de orçamento estão presentes (mensal + por pesquisa)
6. Verifique se o gate de qualidade do CRAG tem um limiar mínimo de nota
7. Verifique se o CRITIC tem o número máximo de iterações definido
8. Verifique se o roteamento multi-modelo especifica o modelo por etapa
9. Verifique se o corpo tem <= 4096 bytes por arquivo

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[research-pipeline-builder]] | downstream | 0.44 |
| p04_cli_research_pipeline_n01 | downstream | 0.38 |
| p02_agent_research_pipeline_intelligence | upstream | 0.36 |
| [[bld_knowledge_research_pipeline]] | upstream | 0.34 |

<!-- cex:domain_contract:start -->
## Domain Contract -- Enforced Rules (real law from the generator)

> Source: `_tools/capability_generators/leadgen.py`'s `domain_contract()` -- read directly from the generator's own module constants (never re-typed by hand, never fabricated). Injected by `_tools/cex_bundle_deepen.py`; re-running regenerates this section idempotently.

**Contract Version**: 1.0.0

### Channels Enum
- b2c_marketplace
- b2b_cnpj
- ugc_social

### Channel Labels
| Key | Value |
|-----|-------|
| b2c_marketplace | B2C marketplace |
| b2b_cnpj | B2B CNPJ |
| ugc_social | UGC social |

### Planned Sources By Channel
- **b2c_marketplace**: mercadolivre.com.br, shopee.com.br
- **b2b_cnpj**: cnpj.gov (Receita/CNPJ), ibge (firmografia)
- **ugc_social**: reddit.com, youtube.com, instagram.com

### Output Section Titles
- Resumo
- Leads
- Proveniencia
- Fontes
- Veredito

### Leads Table Columns
- Nome/Handle
- Tipo
- Canal
- Contato
- Sinal
- Confianca
- Status

### Input Fields
| Key | Value |
|-----|-------|
| objetivo | free text; default placeholder when blank: 'perfil de lead a encontrar' |
| seed | free text (termo/CNPJ/marca); default placeholder when blank: 'termo/CNPJ/marca a pesquisar' |
| regiao | free text; default: 'Brasil' |
| qualificacao | free text; optional, no default (blank allowed) |
| canais | list/CSV from channels_enum; unknown entries dropped honestly (noted); blank/all-invalid -> all channels |
| qtd_alvo | int >= 1; default 25 |
| min_sinais | int >= 1; default 1 (the honesty floor: >=1 signal/source per lead to count) |

### Qualification Gate
| Key | Value |
|-----|-------|
| condition_a_leads_qualificados_floor | leads_qualificados >= min_sinais (per-run floor; default 1) |
| condition_b_confianca_floor | 0.7 |
| condition_c_channel_coverage | at least 1 channel must return data (cobertura_ok) |
| verdict_pass_label | PROSSEGUIR |
| verdict_fail_label | REVISAR |

### Never Fabricate Contract
| Key | Value |
|-----|-------|
| contact_absent_marker | -- |
| rule | unknown name/contact/CNPJ/signal -> field absent or the marker above, NEVER invented (S1-S5, n01_sourcing_rigor) |

### Offline Scaffold
| Key | Value |
|-----|-------|
| example_lead_row_nome | (nenhum lead encontrado) |
| example_lead_row_tipo | -- |
| example_lead_row_contato | -- |
| example_lead_row_score | 0.0 |
| example_lead_row_status | vazio |
| default_when_offline | every selected channel reported blocked (sem credencial); 0 leads, confianca 0.0 |
| default_when_credential_present | phase 1a still reports honest-empty -- real lanes are phase 1b, never fabricated in the meantime |
<!-- cex:domain_contract:end -->
