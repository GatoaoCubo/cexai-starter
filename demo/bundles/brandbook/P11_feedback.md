---
id: bld_feedback_brandbook
kind: quality_gate
pillar: P11
builder: brandbook-builder
version: 1.0.0
quality: null
title: Feedback Gate -- brandbook
author: n06_commercial
tags: [quality_gate, brandbook, P11]
created: 2026-06-22
updated: 2026-06-22
related:
  - p11_qg_builder_nucleus
  - bld_eval_brandbook
  - bld_feedback_default
  - p11_qg_validator
  - bld_eval_default
  - bld_knowledge_card_quality_gate
  - bld_schema_brandbook
  - p11_qg_kind_builder
  - p11_qg_quality_gate
  - p06_td_cex_artifact_type_n03
---

## Gate de Qualidade

quality_floor: 7.0
retry_limit: 2

## Gates Rígidos (FAIL = não publicar)
- H01: frontmatter é válido (id, kind, pillar, quality: null)
- H02: id corresponde ao nome do arquivo
- H03: kind = brandbook
- H04: quality: null (não autoavaliado)
- H05: campos obrigatórios presentes (linha brand_name na seção de identidade)
- H06: corpo <= 8192 bytes
- H07: brand_name presente (específico do kind)

## Gates Flexíveis (WARN = prosseguir + sinalizar)
- H08: > 50% das seções têm conteúdo real (não-placeholder)
- H09: paleta tem pelo menos 1 cor hex real
- H10: arquétipo da persona não é um placeholder
- H11: pelo menos 2 linhas de faça-e-não-faça específicas da marca

## Ciclo de Feedback
Quando a pontuação < 7.0:
1. Reinjetar: solicitar mais materiais ao usuário (URL ou PDF de brand_materials)
2. Rodar o build novamente com os inputs enriquecidos
3. Se a segunda rodada continuar < 7.0: emitir WARN + publicar com quality: null + revision_needed: true

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_builder_nucleus]] | sibling | 0.23 |
| [[bld_eval_brandbook]] | upstream | 0.21 |
| [[bld_feedback_default]] | related | 0.20 |
| [[p11_qg_validator]] | sibling | 0.19 |
| [[bld_eval_default]] | upstream | 0.18 |
| [[bld_knowledge_card_quality_gate]] | related | 0.17 |
| [[bld_schema_brandbook]] | upstream | 0.17 |
| [[p11_qg_kind_builder]] | sibling | 0.16 |
| [[p11_qg_quality_gate]] | sibling | 0.16 |
| [[p06_td_cex_artifact_type_n03]] | upstream | 0.16 |
