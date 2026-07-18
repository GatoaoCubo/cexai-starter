---
kind: instruction
id: bld_instruction_funnel_diag
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo do tool_card da capacidade funnel_diag
pattern: pipeline de 3 fases (mapear -> priorizar -> validar)
quality: null
title: "Instruções: Como Produzir o Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, instruction]
tldr: "3 fases: mapear os 5 estágios com dados do usuário, ranquear consertos por ICE/RICE, validar contra o gate anti-fabricação antes de entregar."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F6_produce"
keywords: [instrução de produção, mapear funil, ranquear consertos, validar diagnóstico, funnel_diag]
density_score: 0.90
related:
  - funnel-diagnostic-builder
  - bld_schema_funnel_diag
---
# Instruções: Como Produzir o tool_card de funnel_diag

## Fase 1: MAPEAR
1. Identifique o produto/serviço e o modelo de negócio (SaaS assinatura, e-commerce, marketplace, serviço) -- isso muda quais métricas fazem sentido por estágio.
2. Pergunte (ou extraia do intent) os dados disponíveis para cada um dos 5 estágios: atrair, engajar, converter, reter, expandir.
3. Para cada estágio sem dado fornecido, registre explicitamente como lacuna -- nunca estime silenciosamente.
4. Quando o usuário não tiver benchmark próprio, ofereça o benchmark público da indústria (rotulado como `estimado`, nunca como medição).
5. Calcule a taxa de queda entre estágios consecutivos sempre que houver volume em ambos os lados.

## Fase 2: PRIORIZAR
1. Liste candidatos a conserto por estágio (mínimo 1 por estágio com dado disponível).
2. Para cada candidato, atribua Impacto (1-10), Confiança (1-10) e Facilidade (1-10) -- ou Alcance x Impacto x Confiança / Esforço se RICE foi escolhido.
3. Calcule o score e ordene do maior para o menor.
4. Verifique o "problema do denominador": um estágio com taxa ruim mas volume pequeno pode ranquear abaixo de um estágio com taxa mediana mas volume grande -- compare perda em números absolutos, não só em percentual.
5. Selecione o(s) 1 a 3 vazamento(s) de maior score para destacar como "vazamento principal".

## Fase 3: VALIDAR
1. [ ] Os 5 estágios foram endereçados (com dado ou com `[A CONFIRMAR]` explícito)?
2. [ ] Cada conserto ranqueado mostra a fórmula e os valores de cada eixo, não só a nota final?
3. [ ] Nenhum número aparece sem origem (`fornecido pelo usuário` / `benchmark público` / `estimado`)?
4. [ ] O vazamento principal está destacado com justificativa numérica, não só qualitativa?
5. [ ] O bloco "Suposições e Dados a Confirmar" está presente e lista toda lacuna?

Se qualquer item falhar, volte à Fase 1 ou 2 antes de entregar.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[funnel-diagnostic-builder]] | downstream | 0.46 |
| [[bld_schema_funnel_diag]] | sibling | 0.38 |
| [[bld_output_template_funnel_diag]] | downstream | 0.34 |

<!-- cex:domain_contract:start -->
## Domain Contract -- Enforced Rules (real law from the generator)

> Source: `_tools/capability_generators/funnel_diag.py`'s `domain_contract()` -- read directly from the generator's own module constants (never re-typed by hand, never fabricated). Injected by `_tools/cex_bundle_deepen.py`; re-running regenerates this section idempotently.

**Contract Version**: 1.0.0

### Input Defaults
| Key | Value |
|-----|-------|
| window_days | 30 |
| health_threshold_pct | 60.0 |
| baseline_window_days | 30 |
| product_label | Funil |

### Canonical Example Funnel
| Stage | Stage Volume |
|-----|-----|
| Visitas | 42000.0 |
| Ver produto | 18480.0 |
| Adicionar ao carro | 5544.0 |
| Iniciar checkout | 2218.0 |
| Compra | 1109.0 |

**Projection Closure Pp**: 5

### Impact Grade Thresholds
| Key | Value |
|-----|-------|
| alto_min_share_of_total_loss | 0.3 |
| medio_min_share_of_total_loss | 0.12 |
<!-- cex:domain_contract:end -->
