---
id: p06_ctx_design_system_pack
kind: context_doc
pillar: P06
nucleus: N03
title: "Design-System Pack -- 30 selectable visual-language archetypes"
version: 1.0.0
created: "2026-07-20"
author: n03_builder
domain: design-systems
scope: REPO
quality: null
tldr: "Catalog of the 30 design_system instances shipped in this pillar: the p06_vs_design_system contract, 20 canonical temperature/density/form archetypes, and 10 vertical applications proving the contract generalizes. Pick one, bind it at F3 INJECT."
tags: [design-system, tokens, index, catalog, leverage]
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Design-System Pack

This pillar ships 31 `design_system`-family artifacts: one governing contract
([[p06_vs_design_system]], `kind: validation_schema`) plus 30 concrete instances
(`kind: design_system`). Every instance conforms to the same five-token-group /
four-recipe / four-rule contract -- only the concrete values differ. A builder
picks exactly ONE instance, binds it at F3 INJECT, and generates the surface from
its tokens alone (see the contract's "How to use" block).

## Provenance

All 30 instances (and the contract) were derived via clean-room concept extraction
from `github.com/nexu-io/open-design` (Apache-2.0) on 2026-06-24. `quality: null` on
every file -- these ship unscored, same as any freshly-produced CEXAI artifact; a
peer-review pass assigns quality, never the producing nucleus itself.

## The two tiers

**Tier 1 -- canonical archetypes (20).** Each one is a pure point on the
temperature x density x form x type coordinate system (no target vertical named in
its `domain:` field -- it says `design-systems`). These are the gravity wells: nearly
every instance in Tier 2, and most instances in the wider 150-file source corpus,
cross-reference back to [[p06_ds_ferro]] (cold/dark/mono anchor) and
[[p06_ds_sereno]] (warm/light/humanist anchor) by name. Pick from this tier when you
want a temperature/mood, not an industry.

| id | Temperature | Density | Signal color | Aesthetic |
|----|---|---|---|---|
| [[p06_ds_abismo]] | dark | comfortable | electric-indigo | cold, dark, airy, geometric void |
| [[p06_ds_alvura]] | light | comfortable | slate-indigo | serene, clinical-calm, luminous |
| [[p06_ds_ardosia]] | dark | compact | sage-citrine | neutral, civic, serif-mono |
| [[p06_ds_areia]] | light | compact | prussian-blue | neutral, civic, geometric |
| [[p06_ds_brasa]] | dark | compact | amber | warm brutalist terminal |
| [[p06_ds_caldo]] | light | comfortable | terracotta | warm, airy, geometric consumer |
| [[p06_ds_crisma]] | light | compact | amber-gold | warm, serif, print-heritage |
| [[p06_ds_cruzo]] | light | compact | tomato-brick | warm, stark, poster grotesque |
| [[p06_ds_estrato]] | dark | comfortable | amber-gold | cold-neutral, mono, dataviz |
| [[p06_ds_ferro]] | dark | compact | teal | engineered, sovereign, terminal-grade (anchor) |
| [[p06_ds_grafeno]] | dark | compact | acid-green | neutral, soft-geometric, dataviz |
| [[p06_ds_granito]] | light | compact | institutional cobalt | cold, stark, civic-grade |
| [[p06_ds_lamina]] | light | compact | indigo | cold, stark, devtools (daylight) |
| [[p06_ds_lastro]] | light | compact | policy-blue | cold, soft-edged, mono civic |
| [[p06_ds_neblina]] | dark | comfortable | icy periwinkle | cold, misty-dark, long-session dashboard |
| [[p06_ds_pulso]] | dark | comfortable | amber-coral | warm, geometric, sonic/audio |
| [[p06_ds_sereno]] | light | comfortable | terracotta | warm, humanist, editorial-calm (anchor) |
| [[p06_ds_vacuo]] | light | comfortable | cobalt-indigo | geometric, grid-strict, editorial-void |
| [[p06_ds_vespera]] | dark | comfortable | amber | candle-lit editorial |
| [[p06_ds_vigil]] | light | comfortable | teal | neutral-balanced, SaaS dashboard workhorse |

**Tier 2 -- vertical applications (10).** Each proves the same contract holds
across a distinct industry: the token groups, component recipes, and usage rules
never change shape -- only the concrete palette, type stack, and motion pacing do.

| id | Domain | Temperature | Signal color | Notable constraint |
|----|---|---|---|---|
| [[p06_ds_capital]] | fintech | dark | mint | mandatory tabular numerals on all money/%/account figures |
| [[p06_ds_amparo]] | telehealth | light | deep teal | error states require icon+label, never color-alone |
| [[p06_ds_fausto]] | luxury-fashion | dark | brushed-gold | 1.414 display scale, slow glide-and-suspend motion |
| [[p06_ds_grao]] | coffee-cafe | light | caramel | handcrafted warmth, gentle-breath enter motion |
| [[p06_ds_catedra]] | e-learning-mooc | light | indigo-blue | secondary `progress` amber token, scoped to the marker recipe only |
| [[p06_ds_voltaico]] | gaming-esports | dark | electric-cyan | glance-speed HUD, zero rounding, magenta reserved for alert only |
| [[p06_ds_termas]] | spa-wellness | light | eucalyptus | unhurried settle motion, stone-warm edge accent |
| [[p06_ds_morada]] | real-estate | light | sage-green | serif display, 56%-image property-card recipe |
| [[p06_ds_alento]] | nonprofit | light | forest-green | donation-progress semantics: always pair % with a plain-language goal |
| [[p06_ds_sintaxe]] | developer-tools | light | indigo | light-mode counterpart to Ferro; code blocks are first-class in the type ramp |

## How to select one

1. Resolve the target `brand_config` identity (temperature, formality, vertical).
2. Match against the tables above -- Tier 1 for a mood/temperature pick, Tier 2 when
   the target vertical has a direct instance.
3. Load exactly one instance at F3 INJECT; bind its tokens as the sole visual source.
4. Never blend two instances in one surface -- the contract's single-signal rule
   applies per generated surface, not per pack.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_design_system]] | upstream -- the contract every instance above conforms to | 0.70 |
| [[p06_ds_ferro]] | anchor -- cold/dark/mono reference point | 0.50 |
| [[p06_ds_sereno]] | anchor -- warm/light/humanist reference point | 0.50 |
