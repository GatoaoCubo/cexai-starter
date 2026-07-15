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
---

## Quality Gate

quality_floor: 7.0
retry_limit: 2

## Hard Gates (FAIL = do not publish)
- H01: frontmatter parses (id, kind, pillar, quality: null)
- H02: id matches filename
- H03: kind = brandbook
- H04: quality: null (not self-scored)
- H05: required fields present (brand_name row in identity section)
- H06: body <= 8192 bytes
- H07: brand_name present (kind-specific)

## Soft Gates (WARN = proceed + flag)
- H08: > 50% sections have real (non-placeholder) content
- H09: palette has at least 1 real hex color
- H10: persona archetype is not a placeholder
- H11: at least 2 brand-specific do/don't rows

## Feedback Loop
On score < 7.0:
1. Re-inject: request more materials from user (brand_materials URL or PDF)
2. Re-run build with enriched inputs
3. If second run still < 7.0: emit WARN + publish with quality: null + revision_needed: true
