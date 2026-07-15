---
id: p01_dq_tenant_intake_form_v2_fields
kind: discovery_questions
pillar: P01
nucleus: n02
title: "Tenant Intake Form v2 -- Field Extension (2026-07-07 GDP)"
version: 1.0.0
created: "2026-07-07"
updated: "2026-07-07"
author: n02_marketing
domain: tenant-onboarding
quality: null
tags: [discovery_questions, intake, onboarding, ingest, v2]
tldr: "15 new OPTIONAL asks (17 keys) added to form_v1 -- all soft-warn; v1's 14 required fields stay the only BLOCK gate."
question_type: "mixed (text/list/enum)"
target_audience: "tenant founder + commercial owner"
sensitivity_level: "low"
related:
  - p01_dq_tenant_intake_form
  - kc_brandbook
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_ingest_registry. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Tenant Intake Form v2 -- Field Extension

## Purpose
Sibling to [[p01_dq_tenant_intake_form]] (each kept at its own ISO ceiling) --
holds the 15 new field ASKS (17 keys) the founder GDP-ratified 2026-07-07.
Source: `docs/PROPOSAL_INTAKE_FORM_V2_2026_07_07.md` (crosswalk vs the founder's
old "Briefing da Marca" form) + `decision_manifest_intake_v2_2026_07_07.yaml`
(DP1-DP5). Resolver: `_tools/cex_ingest_registry.py` (FORM_FIELD_MAP appended,  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
never edited). Fixture: `examples/10_intake_form_v1/form_answers_estufa_aurora_v2.yaml`.

## Scope
All 17 keys are OPTIONAL/soft-warn -- none touch `brand_validate.py`'s required
tier, so a v1 answers file with none of these keys resolves byte-identical
(retro-compat). Skipped honest (no live consumer): "socios/funcionarios?",
"simbolo desejado no logotipo" (fase-3).

## Fields (# = strong, tier=consumer named in the crosswalk; O = optional, tier=weaker)

| # | PT-BR ask | key | type | maps_to | Consumer |
|---|---|---|---|---|---|
| 1 | Principais concorrentes (nomes/links) | `market.competitors` | list | `market.BRAND_COMPETITORS` | N01 competitive_matrix + moldgen benchmark |
| 2 | Faixa de preco esperada (DP2) | `audience.wtp_band` | text `"R$ MIN-MAX"` | `audience.BRAND_WTP_BAND` | `cex_pricing_fastpath.py::parse_wtp_band` (R-132), format-tested |
| 3 | Publico: idade/genero/estilo/interesses | `audience.demographics` | text | `audience.BRAND_DEMOGRAPHICS` | enriches the ICP prompt |
| 4 | Visao da empresa | `identity.vision` | text | `identity.BRAND_VISION` | brandbook builder (visao) |
| 5 | Cores/estilos que NAO quer | `visual.colors_avoid` + `style_avoid` | list x2 | `visual.BRAND_COLORS_AVOID/STYLE_AVOID` | admin theming (D1/D2) + moldgen guard |
| 6 | Estilo de design | `visual.design_style` | soft-enum | `visual.BRAND_DESIGN_STYLE` | theme/landing presets |
| 7 | Ja tem logotipo? (primeiro/renovar) | `visual.logo_status` | enum-2 | `visual.BRAND_LOGO_STATUS` | monogram-automatico (D2 admin theming) |
| 8 | Onde a identidade sera mais usada | `applications.surfaces` | multi | `applications.BRAND_SURFACES` | bootstrap priority (storefront/social/impresso) |
| O1 | Seu nome | `contact.name` | text | `contact.BRAND_CONTACT_NAME` | provenance (quem respondeu) |
| O2 | Seu e-mail | `contact.email` | text | `contact.BRAND_CONTACT_EMAIL` | retorno; never a credential |
| O3 | Razao social (se != fantasia) | `identity.legal_name` | text | `identity.BRAND_LEGAL_NAME` | fiscal/futuro |
| O4 | Cidade / Estado | `location.city_state` | text | `location.BRAND_CITY_STATE` | SEO local / frete |
| O5 | Produtos/servicos que oferece | `positioning.offerings` | text | `positioning.BRAND_OFFERINGS` | copy do storefront |
| O6 | Identidades que admira (links) | `visual.references` | list | `visual.BRAND_REFERENCES` | moodboard / moldgen refs |
| O7 | Admira/supera concorrentes + tendencias | `market.edge_notes` + `trends` | text x2 | `market.BRAND_EDGE_NOTES/TRENDS` | N01 research seeds |

## DP2 -- wtp_band (replaces the old social-class enum)
Ask literally: **"Que faixa de preco seu publico espera pagar?"** Free text
`"R$ MIN-MAX"` (ex.: `"R$ 39-159"`) -- the EXACT shape
`cex_pricing_fastpath.parse_wtp_band` parses (last 2 numbers via regex;
documented fallback when <2 found, never raises). Soft-warn only.

## DP3 -- colors: HEX or description (visual.colors)
`visual.colors` now accepts (a) 3 literal HEX (v1, unchanged, confidence=
`operator`) OR (b) new field `visual.colors_description` (free text) ->
ASSISTED DERIVATION into 3 HEX via a deterministic PT-BR color-keyword table
(never an LLM call), confidence=`derived` (new tier, additive). The
`brand_validate` gate is UNCHANGED -- still requires 3 literal HEX in the
RESULT; an undecidable description leaves `BRAND_COLORS` unset and the gate
correctly fails (input path, never a relaxation). Literal HEX always wins
silently. See `cex_ingest_registry.py::_derive_colors_from_description` +
the mirrored `apps/public_site/lib/intake.ts::deriveColorsFromDescription`.

## Expected Outcomes
Same as v1 (validator-PASS, 14 required + shape) PLUS up to 17 more brand_init
keys w/ provenance (confidence=`operator`, or `derived` for colors-from-
description) when supplied. Fixture `form_answers_estufa_aurora_v2.yaml`
(invented plant-shop brand) exercises 15+ of the 17 keys incl. the derived-
colors path end-to-end.

## Related Artifacts
- [[p01_dq_tenant_intake_form]] (v1 template, upstream)
- [[kc_brandbook]] (upstream)
