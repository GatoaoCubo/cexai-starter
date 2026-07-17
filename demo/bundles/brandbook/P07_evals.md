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
---

## Quality Gates (H07+ kind-specific)

### H07 -- brand_name present
FAIL: brand_name is empty or only placeholders in identity section.
Score penalty: -0.20

### H08 -- at least 5 of 8 sections have real content
WARN: > 50% of section rows are [fornecer: ...] placeholders only.
Score penalty: -0.10 per half-empty section (above 3)

### H09 -- palette section is actionable
WARN: All 5 color rows use [fornecer: hex] placeholders.
Score penalty: -0.10

### H10 -- persona section has archetype
WARN: Arquetipo row is a placeholder.
Score penalty: -0.05

### H11 -- do/don'ts has at least 2 custom rows
INFO: All 4 rows are generic placeholders (brand-specific value not captured).
Score penalty: -0.05

## Scoring Dimensions (5D)
| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| D1 Completeness | 0.30 | % of sections with real (non-placeholder) content |
| D2 Specificity | 0.25 | Placeholders remaining (lower = better) |
| D3 Persona Depth | 0.20 | Archetype + voice + 3 copy samples populated |
| D4 Visual Clarity | 0.15 | Palette + typography populated with real values |
| D5 ROI Framing | 0.10 | Messaging framework maps to real audiences/channels |

## Floor
quality_floor: 7.0 (brandbook is a commercial foundation -- below 7.0 = rework)
