---
id: kc_kind_manifest
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P01
title: "Kind Manifest -- Deep Knowledge for kind_manifest"
version: 1.0.0
created: 2026-07-20
updated: 2026-07-20
author: n03_builder
domain: kind_manifest
quality: null
tags: [kind_manifest, P01, INJECT, kind-kc, per-kind-identity, taxonomy, r-310]
tldr: "Per-kind identity document -- one manifest per registered kind, at kind_{{kind}}/kind_manifest_n00.md, carrying purpose, schema, and builder pointer for that one kind."
when_to_use: "Before authoring a new instance of a registered kind -- read at F3 INJECT to learn that kind's purpose, key fields, and where its builder lives."
keywords: [kind manifest, per-kind identity, canonical manifest, r-310, builder pointer, n00 genesis, taxonomy self-documentation]
density_score: null
related:
  - kind-manifest-builder
  - bld_schema_kind_manifest
  - bld_knowledge_card_kind_manifest
  - n00_knowledge_card_manifest
  - n00_output_template_manifest
---

# Kind Manifest

## Definition
A `kind_manifest` documents ONE registered kind's own identity within the CEX taxonomy: its purpose, key schema fields, and a pointer to its builder (or an honest "not yet built" status). Always scaffolded under `N00_genesis/P0X_*/kind_{{kind}}/kind_manifest_n00.md` -- one manifest per kind, not per instance of that kind. Registered `pillar: P01`, owning `nucleus: N03`, `llm_function: INJECT`, `primary_8f: F3_inject` (`.cex/kinds_meta.json`). A nucleus reads the target kind's manifest before authoring a new artifact of that kind -- same role a `knowledge_card` plays, except the subject is the kind itself, not a world fact.

## Boundaries
**What it is:** the single canonical reference for "what does kind X mean, what fields does it carry, and where does its builder live" -- one document per registered kind (294 real instances as of the R-310 register row; re-verify before citing that count as current, since registering any new kind grows it).

**What it is NOT:**
- NOT `knowledge_card` -- a topic/fact card about the WORLD (e.g. pricing research, a vocabulary term). This was `kind_manifest`'s OWN mis-type until R-310 (2026-07-10) re-typed all 294 instances' `kind:` field -- ids, filenames, and the closed `related:` web stayed byte-unchanged.
- NOT `output_template` -- a kind-builder's F6 PRODUCE artifact shape (with `{{vars}}`, meant to be filled in). `kind_manifest` is F3 INJECT reference material with no fill-in-the-blank body.
- NOT `nucleus_def` -- documents a NUCLEUS (N01-N07), not a kind.
- NOT a builder package's informal "ISO 1" label, nor an independently-registered kind whose OWN name ends in `_manifest` (`deployment_manifest`, `c2pa_manifest`, `fabrication_manifest`, `field_manifest`, `marketplace_app_manifest`). "Manifest" is overloaded 3 ways here -- confirm which sense is meant.

## Naming Convention
| Property | Value |
|---|---|
| Naming pattern | `kind_{{kind}}/kind_manifest_n00.md` -- directory and `id:` vary, filename is INVARIANT |
| ID regex | `^n00_[a-z][a-z0-9_]+_manifest$` (id encodes the TARGET kind: `n00_{{kind}}_manifest`) |
| max_bytes | 8192 (whole file); real corpus observed 3,256-6,352B |
| depends_on | `[]` -- fixed empty; a manifest may reference any kind in prose, no formal dependency edge |
| `nucleus:` inside a produced instance | literal `n00` (lowercase) -- distinct from `kinds_meta.json`'s OWNING nucleus, `N03` |

Never rename the fixed filename or move the `kind_{{kind}}/` directory: `cex_naming_validator.py` skips this filename from its general convention, and `cex_stats.py` counts the parent directory, not the `kind:` field.

## Key Fields
| Field | Type | Required | Notes |
|---|---|---|---|
| id | string | YES | `n00_{{kind}}_manifest` |
| kind | literal `kind_manifest` | YES | -- |
| 8f | literal `F3_inject` | YES | -- |
| pillar | P01-P12 | YES | the DOCUMENTED kind's own pillar, not `kind_manifest`'s own P01 |
| nucleus | literal `n00` | YES | lowercase |
| density_score | float | YES | 294/294 real instances hard-code `1.0` |
| related | list, non-empty | YES | closed, mutual cross-reference web -- do not break by renaming |
| updated | date | REC | 292/294 carry it |

## When to Use
- Before producing a new artifact of a given kind -- read that kind's manifest at F3 to learn its purpose and key fields without opening the full 12-ISO builder set.
- When registering a brand-new kind -- author its manifest as the first F3-facing reference, even before a builder exists (use an honest "Builder -- honest status (register row R-XXX, OPEN)" callout).
- When resolving whether "manifest" in a conversation means this kind, a builder's informal ISO 1, or an independently-registered `*_manifest` kind.

## Related Kinds
- [[bld_schema_output_template]] documents the sibling kind this one is most often confused with (F6 PRODUCE shape vs F3 INJECT reference) -- see `output_template`'s own card for the contrast from its side.
- `nucleus_def` (P02) is the nucleus-level analog: one identity document per NUCLEUS, the same role `kind_manifest` plays per KIND.
- `field_manifest` and the other independently-registered `*_manifest` kinds are unrelated in content (each documents itself, not a taxonomy kind) despite the shared word.

**Honest gap:** `bld_schema_kind_manifest.md` itself (2026-07-10) says "Only ISO 2 exists... the other 11 are a disclosed follow-up" -- a direct directory listing at authoring time shows all 12 ISO files present, so that note is stale; the builder family is complete.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kind-manifest-builder]] | downstream (builder identity) | 0.55 |
| [[bld_schema_kind_manifest]] | downstream (schema, source of truth) | 0.52 |
| [[bld_knowledge_card_kind_manifest]] | sibling (builder's own domain-knowledge ISO) | 0.44 |
| [[n00_knowledge_card_manifest]] | instance (a real manifest this kind governs) | 0.38 |
| [[n00_output_template_manifest]] | related (sibling resolution precedent, R-298/299) | 0.34 |
