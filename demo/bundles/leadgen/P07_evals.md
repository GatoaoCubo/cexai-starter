---
kind: quality_gate
id: p11_qg_research_pipeline
pillar: P11
llm_function: GOVERN
purpose: Exemplos-modelo e anti-exemplos de configs de research pipeline
pattern: aprendizado few-shot -- o LLM le estes exemplos antes de produzir
quality: null
title: "Gate: research_pipeline"
version: 1.0.0
author: n03_engineering
tags: [quality-gate, research-pipeline, P11, STORM, CRAG, CRITIC, governance]
tldr: "Gates para artefatos de research pipeline -- completude das 7 etapas, diversidade de fontes, limiares de CRAG, verificação CRITIC, controles de orçamento."
domain: research_pipeline
created: 2026-03-31
updated: 2026-03-31
8f: "F7_govern"
keywords: [stage completeness, source diversity, crag thresholds, critic verification, budget controls, quality-gate, research-pipeline]
density_score: 1.0
related:
  - research-pipeline-builder
---
## Gate de Qualidade

# Gate: research_pipeline

## Definição
| Campo | Valor |
|-------|-------|
| Kind | research_pipeline (instâncias de cli_tool/workflow) |
| Pillar | P04 (tools) |
| Function | CALL (automação de pesquisa) |
| Limiar | 8.0 mínimo |

## Gates HARD (falha = rejeitado)
| # | Gate | Verificação |
|---|------|-------|
| H1 | 7 etapas completas | Todas as 7 etapas documentadas (de INTENT até VERIFY) |
| H2 | Diversidade de fontes | Pelo menos 2 categorias de fonte preenchidas (mínimo: inbound + search) |
| H3 | Perspectivas STORM | Pelo menos 3 perspectivas definidas com role + focus |
| H4 | Limiar de CRAG | crag_min_score definido (0.0-1.0, padrão 0.7) |
| H5 | CRITIC definido | critic_max_iterations definido; o modelo critic é um modelo de raciocínio |
| H6 | Zero segredos | Nenhuma chave de API em texto plano -- apenas referências a ENV_VAR |
| H7 | Controles de orçamento | Pelo menos 1 teto de orçamento definido (mensal ou por pesquisa) |
| H8 | Roteamento multi-modelo | Pelo menos os modelos extraction + reasoning + critic especificados |

## Gates SOFT (aviso, não rejeita)
| # | Gate | Verificação | Peso |
|---|------|-------|--------|
| S1 | 5+ perspectivas | STORM tem 5+ ângulos de especialista | 0.8 |
| S2 | Cadeias de fallback | Cada fonte tem primária → fallback | 0.9 |
| S3 | Entity resolution | Estratégia de dedup documentada | 0.7 |
| S4 | Schemas de marketplace | Campos de extração por fonte inbound | 0.6 |
| S5 | Formatos de output | 2+ formatos de output (mínimo: html + json) | 0.5 |
| S6 | Pontuação Gartner | Pontuação em 7 dimensões documentada | 0.7 |
| S7 | Rate limits | Rate limits documentados por fonte | 0.6 |
| S8 | Agnóstico de país | Nenhum nome de país/marketplace hardcoded | 0.8 |

## Gate de Qualidade CRAG (por fonte, em runtime)
| Categoria de Fonte | Nota Mínima | Fallback |
|----------------|----------|----------|
| Inbound (marketplace) | 0.7 | Tenta o próximo marketplace → Serper → pula |
| Search (web) | 0.6 | Tenta o próximo motor de busca → pula |
| Outbound (social) | 0.5 | Limiar mais baixo -- dados sociais são ruidosos |
| Trends | 0.4 | Dados de tendência são direcionais, não precisos |
| RAG (interno) | 0.8 | Docs internos devem ter alta qualidade |

## Fórmula de Pontuação
```
score = (HARD_pass / 8) * 6.0 + (SOFT_weighted / max_weight) * 4.0
```

## Níveis de Qualidade
| Nível | Score | Significado |
|------|-------|---------|
| REJECT | < 8.0 | Faltam etapas, sem gates de qualidade, ou violação de segurança |
| PUBLISH | 8.0-8.9 | Pipeline completo, CRAG+CRITIC definidos, orçamento controlado |
| EXEMPLARY | 9.0+ | Catálogo de fontes completo, cadeias de fallback, pontuação Gartner |

## Ações
| Score | Nível | Ação |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publicar como exemplar |
| >= 8.0 | PUBLISH | Pronto para runtime |
| >= 7.0 | REVIEW | Sinalizar para revisão |
| < 7.0  | REJECT | Retrabalho necessário |

## Bypass
| Campo | Valor |
|-------|-------|
| conditions | Artefato research_pipeline experimental sob teste A/B ativo |
| approver | Líder do nucleus (aprovação por escrito obrigatória) |
| audit_trail | Registrar em records/audits/ com o motivo do bypass e timestamp |
| expiry | 48h -- precisa passar em todos os gates antes de expirar |
| never_bypass | H01 (parse do YAML), H05 (quality null) |

## Exemplos

# Exemplos: research-pipeline-builder

## Exemplo Ideal -- E-commerce BR (ACME)
ENTRADA: "Crie uma config de research pipeline para inteligência de marketplace de e-commerce de pets no Brasil"
SAÍDA:
```yaml
identity:
  empresa: "ACME"
  nicho: pet_ecommerce
  idioma: pt-BR
  pais: BR
sources:
  inbound: [mercadolivre, shopee, amazon_br, magalu, americanas, casas_bahia, shein, temu]
  outbound: [youtube, reddit, reclameaqui]
  search: [serper, exa, gemini_search, openai_search]
  trends: [pytrends, keepa]
  rag: [local_docs]
storm_perspectives:
  - {role: buyer, focus: "preco frete reviews confianca"}
  - {role: seller, focus: "positioning pricing quality listing"}
  - {role: analyst, focus: "tendencias volume sazonalidade crescimento"}
  - {role: marketer, focus: "keywords SEO content-gaps social-proof"}
multi_model:
  extraction: gemini-2.5-flash
  reasoning: gpt-5-mini
  social: gemini-2.5-flash
  critic: o4-mini
budget:
  firecrawl_monthly: 3000
  firecrawl_per_research: 10
  serper_daily: 100
output:
  formats: [html, pptx, json]
  idioma: pt-BR
  template: consulting
quality:
  crag_min_score: 0.7
  critic_max_iterations: 3
  final_min_score: 8.0
```
POR QUE É BOM: Todas as categorias de fonte cobertas, perspectivas STORM personalizadas para o nicho, tetos de orçamento definidos, roteamento multi-modelo por tarefa, gates de qualidade explícitos.

## Contraexemplo -- Pesquisa de Fonte Única
```python
# BAD: single source, no quality gate, no verification
results = google_search(query)  # only 1 source
report = gpt4(f"analyze: {results}")  # no CRAG scoring
return report  # no CRITIC verification
```
POR QUE É RUIM: Fonte única (sem STORM), sem gate de qualidade (sem CRAG), sem verificação (sem CRITIC), sem controle de orçamento, sem config.

### S_RELATED: Verificação de Referências Cruzadas (SOFT)
- [ ] campo `related:` do frontmatter preenchido (3-15 entradas)
- [ ] seção `## Related Artifacts` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva a conexão)
