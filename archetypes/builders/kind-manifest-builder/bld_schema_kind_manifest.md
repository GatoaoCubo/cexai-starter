---
kind: schema
id: bld_schema_kind_manifest
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for kind_manifest
pattern: one manifest per registered kind, scaffolded under N00_genesis (R-077/R-298 lineage)
quality: null
title: "Schema Kind Manifest"
version: "1.0.0"
author: n03_builder
tags:
  - "kind_manifest"
  - "builder"
  - "schema"
  - "P01"
tldr: "Field-level source of truth for kind_manifest: the 294-instance real corpus (previously mis-typed knowledge_card, R-310), its id pattern, and the fixed-filename/varying-directory naming convention."
domain: "kind_manifest construction"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F1_constrain"
keywords:
  - "kind manifest construction"
  - "n00_[a-z][a-z0-9_]+_manifest"
  - "id pattern"
  - "R-310"
  - "canonical per-kind manifest"
density_score: 0.90
related:
  - bld_schema_knowledge_card
  - bld_schema_output_template
  - bld_schema_kind
---

# Schema: kind_manifest
## Status (register row R-310, LANDED this pass)
Until now, all 294 real instances carried `kind: knowledge_card` -- a mis-typed
reflexive sub-population the R-307 id-drift measurement flagged EXEMPT-BY-PRECEDENT
pending "an explicit register decision on whether `kind_manifest` should become its own
registered kind" (Section 3b). Founder DP4 approved exactly that
(`decision_manifest_publication_2026_07_10.yaml`). This pass: registered `kind_manifest`
in `.cex/kinds_meta.json`, re-typed the 294 instances' `kind:` field only (ids,
filenames, `related:` webs BYTE-UNCHANGED -- load-bearing, see Naming below), and
authored this ONE ISO. **Only ISO 2 (bld_schema) exists** -- the other 11 (manifest,
system_prompt, instruction, output_template, examples, memory, tools, quality_gate,
knowledge_card, architecture, collaboration, config) are a disclosed follow-up,
mirroring how R-298 registered `output_template` alone and R-299 built its 12-ISO
family separately. Do not assume a full builder exists here beyond this file.

## Disambiguation -- "manifest" is overloaded 3 ways in this codebase
| Sense | What it is | This kind? |
|---|---|---|
| `kind_manifest` (THIS kind) | Per-KIND identity doc: `N00_genesis/P0X_*/kind_{{kind}}/kind_manifest_n00.md`, id `n00_{{kind}}_manifest` | YES (294) |
| Builder-package "ISO 1" | `kind-builder`'s templates informally call a builder set's FIRST ISO "Manifest" (`bld_output_kind.md`) | NO |
| `deployment_manifest`/`c2pa_manifest`/`fabrication_manifest`/`field_manifest`/`marketplace_app_manifest` | Independent kinds whose OWN name ends in "_manifest" | NO -- their KCs are ABOUT them |

## Frontmatter Fields (observed live across all 294 real instances)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | YES | `n00_{{kind}}_manifest` -- 294/294 match. See ID Pattern. |
| kind | literal "kind_manifest" | YES | Re-typed from `knowledge_card` this pass (R-310) |
| 8f | literal "F3_inject" | YES | 294/294 carry exactly this value |
| pillar | string P01-P12 | YES | The DOCUMENTED kind's own pillar (e.g. output_template's manifest carries `pillar: P05`) -- distinct from kinds_meta.json registering `kind_manifest` ITSELF as pillar P01 (a meta-level fact, not a per-instance one) |
| nucleus | literal "n00" | YES | 294/294 (lowercase, unlike kinds_meta.json's `N0X`) |
| title | string | YES | Pattern: `"{{Kind Title}} -- Canonical Manifest"` |
| version | number | YES | Bare `1.0`, not semver-quoted |
| quality | float\|null | YES | Never self-scored |
| tags | list[string] | YES | `[manifest, {{kind}}, {{pillar_lower}}, n00, archetype, template]` |
| density_score | float | YES | 294/294 hard-code exactly `1.0` |
| related | list[string], non-empty | YES | 294/294 populated -- the "closed mutual cross-reference web" R-307 flagged; untouched by this pass |
| updated | date | REC | 292/294 carry it (2 omit -- observed, not enforced) |
| when_to_use, keywords, tldr, open_vars, documents_kind(_pillar) | various | OPT | 2-6/294 each (hand-enrichment, not base convention) |

## ID Pattern
Regex: `^n00_[a-z][a-z0-9_]+_manifest$`
Rule: id encodes the TARGET kind (`n00_{{kind}}_manifest`) -- NOT "id equals filename
stem" (filename is invariant; see Naming below). 294/294 real instances match exactly,
zero exceptions -- only the `kind:` field was ever wrong, never the `id:`.

## Naming (filename fixed, directory + id vary)
Unlike most kinds (`naming` templates the FILENAME), all 294 instances are named
literally `kind_manifest_n00.md` -- zero exceptions. Only the parent directory
(`kind_{{kind}}/`) and the `id:` vary. `kinds_meta.json` registers
`naming: "kind_{{kind}}/kind_manifest_n00.md"` (same shape as `agent_package`'s
`"agents/{{agent_name}}/manifest.yaml"`). **Never rename the filename or move the
directory**: `cex_naming_validator.py` SKIPs this filename from the
`p{{nn}}_{{kind}}_{{descriptor}}_n{{nn}}.ext` convention entirely; `cex_stats.py`'s
`count_kind_manifests_by_pillar()` globs the PARENT DIRECTORY for the `kind_manifests`
badge (294, unchanged -- a directory count, not a `kind:`-field count); the `id:` is a
closed, mutual cross-reference web (`related:` cites sibling ids) -- renaming would
rewrite ~294 files at once (the R-289 trap this row's filing named and avoided).

## No Dedicated Generator (disclosed, not invented)
Repo-wide search (`_tools/*.py`, `*.sh`, `*.ps1`) found no script that WRITES a new
`kind_manifest_n00.md` -- 3 hits, none of them writers: `cex_kind_index_gen.py`
(mentions the path in generated prose), `cex_naming_validator.py` (classifies/skips the
filename), `cex_stats.py` (counts directories). R-298's own register row confirms the
26-manifest sweep was "pattern-first" -- hand-authored, not generated. Forward
correctness is carried by THIS schema (read via F2/F3 before authoring), not a code
gate: an instance authored against it will correctly carry `kind: kind_manifest`.

## Body Structure (required sections, observed in all 294 real instances)
1. `<!-- 8F: F1=... F8=... -->` HTML comment tracing the 8F pipeline for the DOCUMENTED kind
2. `## Purpose` -- 1 paragraph
3. `## Pillar` -- `P0X -- {{pillar_name}}` (one line)
4. `## Schema (key fields)` -- table: Field, Type, Required, Description (documented kind's OWN fields)
5. `## When to use` -- 2-4 bullets (294/294 instances)
6. `## Builder` -- path + `cex_8f_runner.py` example; OR an honest
   "## Builder -- honest status (register row R-XXX, OPEN)" if none exists (1/294 today)
7. `## Template variables (open for instantiation)` -- OPTIONAL, 290/294 instances
8. `## Example (minimal)` -- fenced `yaml`: a minimal instance of the DOCUMENTED kind
9. `## Related kinds` -- bullets, sibling kinds + 1-line contrast
10. `## Related Artifacts` -- wikilink table (relationship + score)

## Constraints
- max_bytes: 8192 (whole file) -- real corpus 3,256-6,352B (p95 4,635B)
- naming: `kind_{{kind}}/kind_manifest_n00.md` (directory varies, filename invariant)
- machine_format: markdown; compiled via `cex_compile.py` -- falls back to `yaml`
  (not yet in `P01_knowledge/_schema.yaml`; `load_schema()` defaults unlisted kinds to
  `yaml` and compiles fine either way -- non-blocking, disclosed)
- depends_on: [] (fixed EMPTY -- a manifest can reference any kind)
- core: false; quality: null always; nucleus: n00 always; 8f: F3_inject always
- NOT `knowledge_card` (fact card about the world; this documents a KIND)
- NOT `output_template` (F6 artifact shape; this is F3 INJECT material)
- NOT `nucleus_def` (documents a NUCLEUS; this documents a KIND)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_knowledge_card]] | contrast (former mis-type, R-310) | 0.46 |
| [[bld_schema_output_template]] | sibling (same resolution shape, R-298/R-299) | 0.40 |
| [[bld_schema_kind]] | related (meta-kind-builder that scaffolds NEW kinds) | 0.33 |
