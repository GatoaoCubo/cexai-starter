---
kind: output_template
id: bld_output_template_roi_calculator
pillar: P05
llm_function: PRODUCE
purpose: Modelo com variáveis para produção de roi_calculator
quality: null
title: "Modelo de Saída -- ROI Calculator"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [roi_calculator, builder, output_template]
tldr: "Modelo com variáveis para produção de roi_calculator"
domain: "construção de roi_calculator"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [construção de roi_calculator, modelo de saída roi calculator, roi_calculator, builder, output_template, modelo anual, parâmetros de entrada, métricas de saída, lucro líquido, investimento total]
density_score: 0.85
related:
  - kc_roi_calculator
  - bld_schema_roi_calculator
  - roi-calculator-builder
---
```yaml
---
id: p11_roi_{{slug}}
kind: roi_calculator
pillar: P11
title: "{{title}}"
version: "1.0.0"
author: "{{author}}"
created: "{{created}}"
updated: "{{updated}}"
domain: "{{domain}}"
quality: null
tags: [{{tags}}]
tldr: "{{tldr}}"
calculation_method: "{{calculation_method}}"
input_parameters: [{{input_parameters}}]
output_metrics: [{{output_metrics}}]
---
```

<!-- slug: identificador em minusculas, ex. saas_platform_3yr ou manufacturing_automation -->
<!-- title: nome descritivo, ex. "ROI da Plataforma SaaS -- Modelo de 3 Anos" -->
<!-- domain: contexto do setor, ex. "SaaS", "manufatura", "saúde" -->
<!-- calculation_method: fórmula usada, ex. "NPV com taxa de desconto de 8%" ou "Forrester TEI" -->
<!-- input_parameters: ["initial_investment", "annual_savings", "implementation_cost", "time_horizon"] -->
<!-- output_metrics: ["roi_percentage", "payback_period_months", "npv", "irr"] -->

## Parâmetros de Entrada

| Parâmetro | Tipo | Unidade | Descrição | Obrigatório |
|-----------|------|------|-------------|----------|
| initial_investment | float | USD | Custo total inicial | sim |
| annual_savings | float | USD | Economia anual de custos | sim |
| implementation_cost | float | USD | Custo único de implantação | sim |
| time_horizon | int | anos | Período de avaliação | sim |
| discount_rate | float | % | Custo de capital (para NPV) | sim |
| annual_maintenance | float | USD | Custos recorrentes da plataforma | sim |

## Métricas de Saída

| Métrica | Fórmula | Limite |
|--------|---------|-----------|
| ROI % | (Lucro Líquido / Investimento Total) * 100 | >= 15% |
| Prazo de Retorno (Payback) | Investimento Total / Economia Anual | <= 24 meses |
| NPV | Soma(Economia / (1+r)^t) - Investimento | > 0 |
| Redução de TCO | TCO da Linha de Base - Novo TCO | > 20% |

## Comparação de Cenários

| Cenário | Ano 1 | Ano 2 | Ano 3 | ROI % |
|----------|--------|--------|--------|-------|
| Conservador | `{{y1_cons}}` | `{{y2_cons}}` | `{{y3_cons}}` | `{{roi_cons}}` |
| Caso Base | `{{y1_base}}` | `{{y2_base}}` | `{{y3_base}}` | `{{roi_base}}` |
| Otimista | `{{y1_opt}}` | `{{y2_opt}}` | `{{y3_opt}}` | `{{roi_opt}}` |

## Premissas

- Taxa de desconto: `{{discount_rate}}`% (WACC ou custo de capital)
- Realização da economia: rampa de adoção de `{{ramp_months}}` meses
- Crescimento da manutenção: `{{maintenance_growth}}`% ao ano
- Fonte: metodologia Forrester TEI / dados validados pelo cliente

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_roi_calculator]] | upstream | 0.38 |
| [[bld_prompt_roi_calculator]] | upstream | 0.36 |
| [[bld_schema_roi_calculator]] | downstream | 0.35 |
| [[bld_knowledge_roi_calculator]] | upstream | 0.35 |
| [[roi-calculator-builder]] | downstream | 0.35 |
