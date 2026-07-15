---
id: kc_brandbook
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P05
title: "Brandbook -- Deep Knowledge for brandbook"
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
domain: brandbook
quality: null
tags: [brandbook, P05, INJECT, kind-kc, brand-identity, never-fabricate, brand-setup]
tldr: "Complete brand OS -- identity+persona+visual+messaging+do/donts assembled into 8 frozen sections from any-media input; composes personality+design_system+white_label_config+tagline, and a PASSING run writes back to become the tenant's live brand config (B2 seam)."
when_to_use: "Building, reviewing, or reasoning about brandbook artifacts"
keywords: [brandbook, brand book, brand identity, brand persona, brand voice, color palette, typography, logo usage, imagery style, messaging framework, do and donts, never-fabricate, brand-setup, moldgen overlay, honest placeholder]
feeds_kinds: [brandbook]
density_score: 0.95
related:
  - brandbook-builder
  - bld_output_brandbook
  - bld_knowledge_brandbook
  - p12_ct_brand_discovery
  - kc_personality
  - p01_kc_design_system
  - kc_white_label_config
  - kc_tagline
---

# Brandbook

## Spec
```yaml
kind: brandbook
pillar: P05
llm_function: PRODUCE
max_bytes: 8192
naming: p05_bb_{{brand}}.md
core: false
requires_external_context: true
depends_on: [personality, design_system, white_label_config, tagline]
```
Source: `.cex/kinds_meta.json` entry for `brandbook`.

## What It Is
A `brandbook` (P05) is the **complete brand book**: identity + color palette +
typography + brand persona (voice/tone/copy) + logo usage + imagery style +
messaging framework + do/don'ts -- assembled from any-media input (brand PDF,
logo PNG, site URL, or a guided description) into 8 frozen sections. Per
`.cex/kinds_meta.json` boundary: "Complete brand book -- identity+persona+voice
+visual+messaging+do/donts; NOT brand_config (a single platform identity
record) nor design_system (tokens only without persona or messaging)."

NOT `design_system` (P06) -- concrete color/type/space/motion/form tokens +
component recipes only; no persona, no messaging framework.
NOT `white_label_config` (P09) -- the 24 HSL brand tokens + reseller/API/UX
config surface, not the full identity/persona/messaging surface.
NOT `personality` (P02) -- one hot-swappable voice/tone/values overlay; the
brandbook's Persona section is one of 8 sections, not the whole artifact.
NOT `tagline` (P03) -- a single positioning line; the brandbook's Identity
section *consumes* one, it doesn't define the tagline format.
NOT `brand_config` -- not a kind in the 300+ taxonomy at all; it is the
tenant's single platform-identity record (`.cex/brand/brand_config.yaml`, or
the per-tenant moldgen overlay) that a PASSING brandbook run *writes into*
(see "Brand-setup write-back" below).

There is no `p06_vs_brandbook` validation_schema instance in this repo today
(verified: no `p06_vs_brandbook*` or `spec_brandbook*` file exists). The
closest thing to a formal contract is [[bld_output_brandbook]] (kind:
response_format), which fixes the frontmatter + section layout.

## 8 frozen sections (builder and capability paths agree)
| # | Section | Layout | Key rows/cols |
|---|---------|--------|---------------|
| 1 | Identidade da Marca | fields | Nome, Essencia, Proposta de valor, Posicionamento, Missao, Valores |
| 2 | Paleta de Cores | table | Funcao \| Hex \| Contraste \| Uso principal (5 roles: Primaria/Secundaria/Destaque/Neutra/Fundo) |
| 3 | Tipografia | fields | Primaria (headings), Secundaria (corpo), Display/especial, Escala de tamanhos |
| 4 | Persona da Marca | fields | Arquetipo, Voz, Tom geral, Tom em crises, 3 copy samples (headline/beneficio/CTA) |
| 5 | Uso do Logotipo | list | versao principal/escura, espaco de protecao, tamanho minimo, distorcoes proibidas, versoes nao aprovadas |
| 6 | Estilo de Imagem | fields | Mood geral, Estilo de fotografia, Paleta de filtros, Elementos proibidos |
| 7 | Framework de Mensagem | table | Mensagem \| Publico-alvo \| Canal \| Prioridade |
| 8 | Dos e Nao-Faca | table | Fazer \| Nao Fazer |

Order is FROZEN identically in both authoring surfaces: the builder prompt
(`bld_prompt_brandbook.md`, "Section Order (F6, FROZEN)") and the runtime
generator (`_tools/capability_generators/brandbook.py`, functions `s1`..`s8`).

## Two production paths, one shape
| Path | Entry point | Output |
|------|-------------|--------|
| Builder (.md artifact) | [[brandbook-builder]] (`archetypes/builders/brandbook-builder/`, 12 ISOs), naming `p05_bb_{brand_slug}.md` | Static P05 artifact, frontmatter `kind: brandbook`, `nucleus: N06` |
| Capability (dashboard) | `_tools/capability_generators/brandbook.py`, `@register("brandbook")`, routed via `_tools/cex_run_capability.py` (`"brandbook": ("N06", "brandbook", "P05", "create")`) | `structured_output()` dual-output payload (human_html + machine .md); `RUN_MODE = "offline-scaffold"` |

No `p05_bb_*.md` instance exists yet under any `N0*/` directory in this repo
(verified: `find N0* -iname "p05_bb_*"` returns nothing). Every brandbook
produced so far runs through the capability path, not a hand-authored
builder artifact.

## Input contract (MoldField[], from `bld_schema_brandbook.md`)
| Key | Required | Cell A pre-processing |
|-----|----------|------------------------|
| brand_name | yes | -- |
| brand_essence | no | -- |
| brand_materials | no | file/url/text |
| brand_materials_text | no | extracted from PDF/URL by Cell A |
| brand_materials_palette | no | hex list extracted from logo/image |
| brand_materials_data_uri | no | uploaded image -> `produced_media["logo_primary"]` |

## NEVER-FABRICATE convention
A field without source data renders `[fornecer: {description}]` ("please
provide", pt-BR) instead of an invented value -- no guessed brand colors,
font names, copy samples, or conversion metrics. Enforced in both surfaces:
the builder prompt states it as a rule; the generator enforces it
mechanically (`_parse_palette` only accepts strings matching `_HEX_RE`, a
6-digit hex regex -- a bad token is dropped, never guessed).

## Composition: what a brandbook consumes
| Kind | Pillar | Role | Direction |
|------|--------|------|-----------|
| [[kc_tagline|tagline]] | P03 | positioning line -> Identity section | consumes |
| [[kc_personality|personality]] | P02 | voice/tone/archetype -> Persona section | consumes |
| [[p01_kc_design_system|design_system]] | P06 | color/type tokens -> Paleta + Tipografia sections | consumes |
| [[kc_white_label_config|white_label_config]] | P09 | 24 HSL brand tokens -> Paleta + Tipografia sections | consumes |

(`depends_on` per `.cex/kinds_meta.json`: personality, design_system,
white_label_config, tagline -- all four.)

The `brand_discovery` crew (p12_ct_brand_discovery, 3-role sequential:
`p02_ra_brand_strategist` -> `p02_ra_persona_architect` -> `p02_ra_visual_packager`)
is the authoring topology that produces the upstream artifacts and assembles
the brandbook. `p02_ra_visual_packager`'s goal is literally "Assemble the
final brandbook by composing palette + typography + persona + positioning
into p05_bb_{brand}.md"; its backstory: "you do NOT invent brand values or
colors... you orchestrate the composition of personality + design_system +
white_label_config into a single, structured, publish-ready brandbook."

## Brand-setup write-back (B2 seam) -- brandbook's unique downstream effect
Unlike most P05 kinds, a PASSING `brandbook` capability run does not just sit
as an artifact -- it BECOMES the tenant's live brand config. `_tools/cex_run_capability.py`
(guarded `if cap == "brandbook" and passed:`) calls
`_tools/cex_brand_writeback.py::write_brand_overlay`, which maps the
structured output to the tenant's moldgen overlay:

| Brandbook field | Moldgen spec target |
|------------------|----------------------|
| brand_name | spec name / nameHtml |
| brand_essence | spec tagline |
| palette[0..4] | primary/secondary/highlight/muted/foreground HSL tokens (unset roles fall back to the shared neutral baseline) |
| logo data-uri | spec logo |

A missing/unparseable brand_name REFUSES the write (never a nameless brand
config); a hex that fails to parse is SKIPPED, never guessed. After the
write, `cex_brand_context.resolve_brand_context` returns the NEW brand and
every OTHER capability re-personalizes from it (the open-mustache invariant:
brand values are never hardcoded). This is why `brandbook` is listed in
`_tools/cex_capability_registry.py::_DEFAULT_SENSITIVE_CAPABILITIES` --
"paid LLM (full brand book)" -- alongside `research`, `ads`, and `landing`. A
companion module, `_tools/cex_brand_extract.py`, lets a tenant skip the
hand-built brandbook entirely by extracting a palette from a live site URL,
reusing the SAME hex-to-HSL mapping so both paths land on identical tokens.

## Quality gates (H07-H11, from `bld_eval_brandbook.md`)
| Gate | Rule | Penalty |
|------|------|---------|
| H07 | brand_name present | -0.20 (FAIL if missing) |
| H08 | >= 5 of 8 sections carry real (non-placeholder) content | -0.10 per half-empty section above 3 |
| H09 | palette section is actionable (not all 5 rows `[fornecer: hex]`) | -0.10 |
| H10 | persona Arquetipo row is not a placeholder | -0.05 |
| H11 | do/don'ts has >= 2 custom (non-generic) rows | -0.05 |

5D weights: D1 Completeness 0.30, D2 Specificity 0.25, D3 Persona Depth 0.20,
D4 Visual Clarity 0.15, D5 ROI Framing 0.10. `quality_floor: 7.0` ("brandbook
is a commercial foundation -- below 7.0 = rework").

The runtime generator computes its own, looser bar independently: score
starts at 1.0, same-shaped deductions (-0.20 missing brand_name, -0.10 no
palette, -0.10 no materials text, -0.05 no essence), `passed = (not missing)
and score >= 0.60`. The generator's 0.60 gate targets always-on scaffold
availability (never block on missing optionals); the builder's 7.0 floor
targets final-publish quality -- the two are complementary, not contradictory.

## Anti-patterns
| Anti-pattern | Why it fails |
|---------------|---------------|
| Inventing a hex, font name, or copy sample when materials are missing | Breaks NEVER-FABRICATE; emit `[fornecer: ...]` instead |
| Treating brandbook as a single-kind artifact | It composes 4 kinds (tagline/personality/design_system/white_label_config); building it standalone without those upstream artifacts starves the persona/visual sections |
| Confusing brandbook with brand_config | `brand_config` is the tenant's single platform-identity record (not a kind in the taxonomy); `brandbook` is the authored source that *writes into it* via the B2 seam |
| Writing back on a FAILING run | The write is gated on `passed`; a half-built or nameless brandbook must never overwrite a tenant's live brand |
| `quality` set to a score | Never self-score; peer review assigns (H04 universal gate) |

## Quality criteria
- GOOD: all 8 sections present in frozen order, brand_name resolved, >= 5
  sections carry real (non-placeholder) content.
- GREAT: palette extracted (not all placeholders), persona archetype + all 3
  copy samples populated, do/don'ts has >= 2 brand-specific rows, H07-H11 all
  pass (quality >= 7.0).
- FAIL: brand_name missing or placeholder-only, `quality` not null, any of
  the 8 sections silently dropped from the frozen order.

## Integration graph
```
[tagline (P03)]            --consumed by--> [brandbook Sec.1 Identidade]
[personality (P02)]        --consumed by--> [brandbook Sec.4 Persona]
[design_system (P06)]      --consumed by--> [brandbook Sec.2+3]
[white_label_config (P09)] --consumed by--> [brandbook Sec.2+3]
[p12_ct_brand_discovery crew] --assembles--> [brandbook]
[brandbook PASSING run] --B2 write-back--> [tenant moldgen overlay / brand config]
[tenant moldgen overlay] --re-personalizes--> [every other capability]
```

## Decision tree
- IF you need the COMPLETE brand identity surface (identity + visual + voice
  + messaging + guardrails) THEN `brandbook` (P05).
- IF you need only the color/type/space/motion/form tokens THEN
  `design_system` (P06).
- IF you need only the 24 HSL reseller tokens for a white-label deployment
  THEN `white_label_config` (P09).
- IF you need only the hot-swappable voice/tone overlay THEN `personality`
  (P02).
- IF you need only a single positioning line THEN `tagline` (P03).
- DEFAULT: `brandbook` when the deliverable must drive brand consistency
  across ALL revenue-generating channels -- per `bld_model_brandbook.md`
  (Strategic Greed / N06 lens): "Inconsistent brand = lost conversion."

## Related Artifacts
| Artifact | Relationship | Score |
|----------|--------------|-------|
| [[brandbook-builder]] | downstream (builder, 12 ISOs) | 0.55 |
| [[bld_output_brandbook]] | upstream (output contract) | 0.50 |
| [[bld_knowledge_brandbook]] | sibling (domain knowledge ISO) | 0.42 |
| p12_ct_brand_discovery | sibling (authoring crew) | 0.42 |
| [[kc_personality]] | peer (composed kind) | 0.32 |
| [[p01_kc_design_system]] | peer (composed kind) | 0.30 |
| [[kc_white_label_config]] | peer (composed kind) | 0.28 |
| [[kc_tagline]] | peer (composed kind) | 0.26 |
