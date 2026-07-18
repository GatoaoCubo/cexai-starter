---
id: bld_eval_brandbook
kind: scoring_rubric
pillar: P07
builder: brandbook-builder
version: 1.0.0
quality: null
title: Eval -- brandbook
author: n06_commercial
tags: [scoring_rubric, brandbook, P07, quality_gate]
llm_function: GOVERN
created: 2026-06-22
updated: 2026-06-22
related:
  - bld_feedback_brandbook
  - bld_prompt_brandbook
---

## Gates de Qualidade (H07+ específicos do kind)

### H07 -- brand_name presente
FAIL: brand_name está vazio ou contém apenas placeholders na seção de identidade.
Penalidade de pontuação: -0.20

### H08 -- pelo menos 5 das 8 seções têm conteúdo real
WARN: > 50% das linhas de seção são apenas placeholders [fornecer: ...].
Penalidade de pontuação: -0.10 por seção meio-vazia (acima de 3)

### H09 -- seção de paleta é acionável
WARN: As 5 linhas de cor usam placeholders [fornecer: hex].
Penalidade de pontuação: -0.10

### H10 -- seção de persona tem arquétipo
WARN: A linha Arquétipo é um placeholder.
Penalidade de pontuação: -0.05

### H11 -- faça-e-não-faça tem pelo menos 2 linhas customizadas
INFO: As 4 linhas são placeholders genéricos (valor específico da marca não capturado).
Penalidade de pontuação: -0.05

## Dimensões de Pontuação (5D)
| Dimensão | Peso | O Que Mede |
|----------|------|------------|
| D1 Completude | 0.30 | % de seções com conteúdo real (não-placeholder) |
| D2 Especificidade | 0.25 | Placeholders restantes (menor = melhor) |
| D3 Profundidade da Persona | 0.20 | Arquétipo + voz + 3 exemplos de copy preenchidos |
| D4 Clareza Visual | 0.15 | Paleta + tipografia preenchidas com valores reais |
| D5 Enquadramento de ROI | 0.10 | Framework de mensagem mapeia para públicos/canais reais |

## Piso
quality_floor: 7.0 (brandbook é uma fundação comercial -- abaixo de 7.0 = retrabalho)

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_feedback_brandbook]] | downstream | 0.21 |
| [[bld_prompt_brandbook]] | upstream | 0.16 |
