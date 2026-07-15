---
id: p01_dq_tenant_intake_form
kind: discovery_questions
pillar: P01
nucleus: n02
title: "Tenant Intake Form v2 (R-149 + v2 GDP 2026-07-07)"
version: 2.0.0
created: "2026-07-06"
updated: "2026-07-07"
author: n02_marketing
domain: tenant-onboarding
quality: null
tags: [discovery_questions, intake, onboarding, ingest, v2]
tldr: "Intake bank PT-BR/EN: 3 personas x 3 stages -> ONE brand_config.yaml every consumer parses. v2: +15 optional asks, see sibling."
question_type: "mixed (text/enum/int/hex/url/list/file)"
target_audience: "tenant founder + commercial owner + ops owner"
sensitivity_level: "medium (creds: env refs only, R-276)"
related:
  - kc_brandbook
  - bld_schema_brandbook
  - p01_dq_cexai_implementation_services
  - p01_dq_tenant_intake_form_v2_fields
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_ingest_registry. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Tenant Intake Form v2 (R-149 + v2 GDP 2026-07-07)

## Purpose
Uma entrevista -> `brand_init.yaml` consumido por `cex_bootstrap --from-file`, `cex_tenant_bootstrap --spec`, `cex_distill --from-tenant/--shape`. Resolver: `_tools/cex_ingest_registry.py`. Evidencia+exemplos: `docs/SPEC_INTAKE_FORM_V1_2026_07_06.md` + `docs/SPEC_INTAKE_FORM_V2_2026_07_07.md`; fixtures: `examples/10_intake_form_v1/`.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

## Scope
In: campos abaixo (todos com consumidor vivo) + 15 novos OPCIONAIS/soft-warn
em [[p01_dq_tenant_intake_form_v2_fields]] (competitors/wtp_band/demographics/
vision/colors_avoid+style_avoid/design_style/logo_status/surfaces + 7 mais --
founder GDP 2026-07-07). Os 14 `*` abaixo continuam o UNICO gate BLOCK; v1
sozinho permanece um subconjunto valido de v2 (retro-compat). Out (fase-2):
storefront content, catalog/CRM importers, repo S4.

## Question Formulation
S1 INGEST -> S2 SHAPE -> S3 BOOTSTRAP. `*` = obrigatorio (= gate brand_validate).

### Persona A -- Fundador(a) [S1->S3]
| Pergunta | key | tipo | maps_to |
|---|---|---|---|
| *Nome da marca? | brand_name | text | identity.BRAND_NAME |
| *Tagline (10-100)? | brand_tagline | text | identity.BRAND_TAGLINE |
| *Missao (por que)? | brand_mission | text | identity.BRAND_MISSION |
| *3-5 valores | brand_values | list | identity.BRAND_VALUES |
| Historia da marca | brand_story | text | identity.BRAND_STORY |
| *Arquetipo (12) | brand_archetype | enum | archetype.BRAND_ARCHETYPE |
| *Tom de voz | voice.tone | text | voice.BRAND_VOICE_TONE |
| *Formalidade 1-5 | voice.formality | int | voice.BRAND_VOICE_FORMALITY |
| Idioma xx-XX | voice.language | text | voice.BRAND_LANGUAGE |
| Sempre/nunca (3+3) | voice.do/dont | list | voice.BRAND_VOICE_DO/DONT |
| *Cliente ideal (20+) | audience.icp | text | audience.BRAND_ICP |
| *From X to Y through Z | audience.transformation | text | audience.BRAND_TRANSFORMATION |
| *3 cores HEX | visual.colors | hex | visual.BRAND_COLORS |
| Logo | visual.logo | url/file | visual.BRAND_LOGO_URL |
| Fontes | visual.fonts | list | visual.BRAND_FONTS |
| *Categoria | positioning.category | text | positioning.BRAND_CATEGORY |
| *UVP (20+) | positioning.uvp | text | positioning.BRAND_UVP |
| Pilares de conteudo | positioning.content_pillars | list | positioning.BRAND_CONTENT_PILLARS |

### Persona B -- Comercial [S2]
| Pergunta | key | tipo | maps_to |
|---|---|---|---|
| *Modelo de preco (6) | monetization.pricing_model | enum | monetization.BRAND_PRICING_MODEL |
| *Moeda | monetization.currency | text | monetization.BRAND_CURRENCY |
| Tiers b2c-*/b2b-*/mkt-* | monetization.tiers | list | monetization.BRAND_TIERS |
| Canais de venda | location.channels | list | location.BRAND_CHANNELS |
| Confirma vertical/loja/blog/b2b? | shape_confirm.* | enum | 9-key shape |
| 9 links https | links.* | url | tenant links (spec WINS) |
| Slug | tenant.slug | text | --tenant SLUG |

### Persona C -- Operacao [S1]
| Pergunta | key | tipo | maps_to |
|---|---|---|---|
| URL do site | sources.site_url | url | extractor url |
| Snapshot HTML/PDF | sources.snapshot | file | extractor html/pdf |
| Ja tem brandbook? | sources.brandbook | file/url | extractor pdf/html |
| Catalogo (ref) FASE-2 | catalog.source_ref | text | R-165 importer slot |
| CRM FASE-2: so env-var (R-276) | credentials.crm_ref | text | .env ref; literal=DROPPED |

## Target Audience
A=founder; B=comercial; C=ops. Uma pessoa pode responder tudo.

## Expected Outcomes
brand_init validator-PASS (14 required) + shape committed + provenance por campo.
v2: idem, + ate 17 campos opcionais quando preenchidos (nunca bloqueia).

## Review Process
1. Founder valida a lista. 2. Peer review. 3. Fixture E2E verde.

## v2 Changelog (2026-07-07)
+15 asks opcionais (17 keys) via GDP -- ver [[p01_dq_tenant_intake_form_v2_fields]].
DP2: pergunta de classe social virou `audience.wtp_band` (faixa de preco).
DP3: `visual.colors` aceita HEX ou descricao (derivacao assistida, confidence=derived).
Canal: `/intake` (apps/public_site) continua o canonico (DP4).

## Related Artifacts
- [[kc_brandbook]] (upstream)
- [[bld_schema_brandbook]] (upstream)
- [[p01_dq_tenant_intake_form_v2_fields]] (v2 field extension)
- [[p01_dq_cexai_implementation_services]] (sibling)
