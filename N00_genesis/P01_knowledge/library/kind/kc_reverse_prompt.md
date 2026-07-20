---
id: p01_kc_reverse_prompt
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P03
title: "reverse_prompt: Repo-Reconstruction Prompt Artifact"
version: 1.0.1
created: 2026-05-27
updated: 2026-07-03
author: n04
domain: reverse_prompt
quality: null
open_vars: []
tags: [reverse_prompt, p03, PRODUCE, kind-kc, reposynth, gitreverse]
tldr: "A typed, persisted repo-reconstruction PROMPT synthesized from a public repo -- a single artifact whose body instructs a downstream LLM to rebuild an equivalent project, calibrated by 3 open_vars (target_audience, target_runtime, complexity_level)"
when_to_use: "Building, reviewing, or reasoning about reverse_prompt artifacts emitted by the repo_synthesizer tool (vertical 14)"
keywords: [reverse-prompt, repo-synthesis, reconstruction, gitreverse, triangulation-source, open-vars, deterministic]
feeds_kinds: [reverse_prompt]
density_score: null
related:
  - knowledge_card
  - p01_kc_prompt_template
  - p01_kc_rag_source
  - p01_kc_citation
  - p01_kc_prompt_compiler
  - reverse-prompt-builder
  - adr_v04_tools_taxonomy
---

# Reverse Prompt

## Spec
```yaml
kind: reverse_prompt
pillar: P03
llm_function: PRODUCE
primary_8f: F6_produce
max_bytes: 8192
naming: p03_rp_{{name}}.md
core: false
depends_on: [prompt_template]
```

## What It Is
A `reverse_prompt` is the typed, persisted artifact a repo synthesizer EMITS when
it converts a public source-code repository into a single reusable prompt. Its
body is a repo-reconstruction prompt: instructions detailed enough that a
downstream LLM can rebuild an equivalent project, OR fold the repo's structure
into research context, without re-fetching the repo each time.

It is the OUTPUT of filling a fixed synthesis `prompt_template` (FR-006) with an
extracted `RepoExtract` (metadata + sorted file tree + README + up to 10
entry-point files) and three resolved open_vars. The persisted `.md` lives at
`.cex/runtime/artifacts/reverse_prompts/<tree_sha>.md` with full frontmatter
(`kind: reverse_prompt`, `open_vars`, `source_url`, `tree_sha`).

It is NOT a reusable template and NOT a factual note. It is a single synthesized,
frozen, provenance-bearing prompt instance, deterministic for a given
`(tree_sha, filled_open_vars)` tuple.

Spec provenance: `cexai-specs/14_gitreverse/spec.md` US P1/P2/P3 +
FR-002/004/005/006/013. Runtime shape: the frozen dataclass
`cexai.tools._shared.types.ReversePrompt` (source_url, tree_sha, open_vars,
filled_vars, body, frontmatter). Prior art (technique only, clean-room,
Apache-2.0): the `gitreverse` project; no source inspected.

## Boundary (read before building)
| Kind | Pillar | Role | Cardinality | Lifetime |
|------|--------|------|-------------|----------|
| `prompt_template` | P03 | The reusable TEMPLATE with `{{vars}}` to generate prompts | One per topic | Durable authored artifact |
| `reverse_prompt` | P03 | The synthesized INSTANCE: one repo rendered into a filled, frozen reconstruction prompt | Many (one per `(tree_sha, open_vars)`) | Emitted runtime artifact |
| `knowledge_card` | P01 | A FACTUAL note distilling knowledge about a topic | One per topic | Durable authored artifact |

In one sentence: `prompt_template` is the *mold* the synthesizer fills,
`reverse_prompt` *is one repo poured into that mold and frozen*, and
`knowledge_card` is *a fact you wrote down*, not a generative prompt.

## Key Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source_url | string | yes | Canonical repo URL (github/gitlab/bitbucket or `<owner>/<repo>` shorthand, FR-001) |
| tree_sha | string | yes | Platform tree SHA of the default branch at fetch time -- the cache + determinism key (FR-003/006) |
| open_vars | list | yes | The 3 declared open-var names (FR-005); always `[target_audience, target_runtime, complexity_level]` |
| filled_vars | map | yes | Resolved `name -> value` (the frozen `_filled_vars` per ADR 022) |
| body | string | yes | The synthesized reconstruction prompt |
| frontmatter | map | yes | Artifact frontmatter (kind, source_url, tree_sha, synthesized_at, provenance) |

## The 3 open_vars (FR-005, Article XIX)
| open_var | Type | Filler role | Default |
|----------|------|-------------|---------|
| `target_audience` | str | compiler or user | via `brand_config.target_audience` |
| `target_runtime` | enum: claude-code \| codex \| gemini \| ollama | compiler | resolved at synthesis |
| `complexity_level` | enum: introductory \| intermediate \| advanced | user (via GDP) | intermediate |

`target_audience` and `complexity_level` are `rebind_allowed: true` (same repo,
different audience is a rebind, not a re-synthesis). `target_runtime` is
`rebind_allowed: false` (cross-runtime is a fresh deterministic synthesis, not a
rebind) -- FR-014.

## Cross-Framework Map
| Framework/Concept | Closest Concept | Notes |
|-------------------|-----------------|-------|
| gitreverse (prior art) | repo -> reusable prompt | The absorbed technique this kind documents (clean-room, technique only) |
| RAG ingestion | a source document chunk | reverse_prompt is a 4th triangulation source alongside scrapling/claude-mem/welib (US P2) |
| Code summarization (e.g. repo digesters) | a one-shot repo summary | reverse_prompt is a *reconstruction* prompt, calibrated by open_vars, not a flat summary |
| Prompt instantiation | a filled template | reverse_prompt = `prompt_template` filled with a `RepoExtract` + open_vars and frozen |

## Patterns
| Pattern | When to Use | Example |
|---------|-------------|---------|
| Reconstruction prompt | Rebuild an equivalent project from a reference repo | Feed the body to a fresh LLM to scaffold a clone |
| Triangulation source | Enrich a research intent that names a repo | Synthesizer returns cached/fresh reverse_prompt within the 3s source budget (US P2) |
| Audience recalibration | Same repo, different consumer | Rebind `target_audience`/`complexity_level`; reuse the cached `tree_sha` extract |
| License-gated synthesis | Declared downstream license | `--downstream-license MIT` fails closed on a GPL-3.0 upstream (E2) |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Treating a builder-authored draft as a REAL synthesis | The determinism guarantee (temp 0.0, sorted extraction) is a property of `GitReverseSynthesizer`, not of any LLM-authored text | For a REAL repo, run `cexai repo_synthesizer create <url>`. A NARROW `reverse-prompt-builder` was scaffolded 2026-07-03 (`docs/DECISION_BUILDERLESS_KINDS_2026_07_03.md`) for documentation/dry-run/repair/calibration ONLY -- see its bld_model Provenance Note. See "Builder Note" below. |
| Modeling it as a `prompt_template` | A template is reusable + unfilled; a reverse_prompt is a filled, frozen instance | Author the template once; let the synthesizer emit instances |
| Modeling it as a `knowledge_card` | A KC is a factual note, not a generative reconstruction prompt | Use `knowledge_card` for facts; `reverse_prompt` for repo->prompt synthesis |
| Mutating a frozen reverse_prompt | Output is deterministic for `(tree_sha, filled_vars)`; mutation breaks idempotency (FR-006) | Re-synthesize with new inputs (new `tree_sha` or rebound open_vars) |
| Silently synthesizing a no-LICENSE repo as permitted | Legal-hygiene gate (Article XVII) | Emit `LicenseUnknownWarning` + mark `derived_from_unlicensed_source: true` (E3) |

## Integration Graph
```
[public repo URL] --extract--> [RepoExtract (metadata + sorted tree + README + <=10 entry files)]
                                         |
              [prompt_template (fixed synthesis template)] + [3 open_vars filled]
                                         |
                              router.dispatch(temp=0.0)   (FR-012, deterministic)
                                         |
                                         v
                 [reverse_prompt artifact .md @ .cex/runtime/artifacts/reverse_prompts/<tree_sha>.md]
                                         |
                          +--------------+--------------+
                          |                             |
              (downstream reconstruction)     (4th triangulation source -> compiler Layer-1)
```

## Decision Tree
- IF you are authoring a REUSABLE prompt with `{{vars}}` -> that is a
  `prompt_template`, NOT a reverse_prompt.
- IF you are recording a FACT about a repo or topic -> that is a
  `knowledge_card`, NOT a reverse_prompt.
- IF you converted a specific public repo into a single filled, frozen
  reconstruction prompt -> this is a `reverse_prompt` instance (emitted by the
  synthesizer at runtime).
- DEFAULT: a reverse_prompt is RUNTIME-EMITTED by the `repo_synthesizer` tool
  (vertical 14) -- this remains the CANONICAL, deterministic path for a REAL
  synthesis. A NARROW `reverse-prompt-builder` (scaffolded 2026-07-03, see
  "Builder Note" below) exists ONLY for documentation/dry-run/repair/calibration
  drafts and never substitutes for a real synthesis.

## Quality Criteria
- GOOD: source_url + tree_sha + the 3 open_vars declared + frozen filled_vars +
  body present; deterministic for the `(tree_sha, filled_vars)` tuple.
- GREAT: provenance complete (synthesized_at, synthesized_by_nucleus); license
  evaluated (compatible, or `derived_from_unlicensed_source` marked); truncation
  flagged (`_extraction_truncated`) when the file-count budget is hit; the body
  is calibrated to the filled open_vars (not a one-size blob).
- FAIL: non-deterministic output for identical inputs; missing provenance;
  modeled as a template or a factual note; synthesized past a fail-closed license
  gate.

## Builder Note (added 2026-07-03 -- read alongside kind_manifest_n00.md's "Emission" section)
A `reverse-prompt-builder` (12 ISOs, `archetypes/builders/reverse-prompt-builder/`)
was scaffolded 2026-07-03 per `docs/DECISION_BUILDERLESS_KINDS_2026_07_03.md`
(SCAFFOLD verdict, GDP-closed) to give a free-form "build me a reverse_prompt"
intent an F2 BECOME target instead of a dead end. **This partially revises** the
`adr_v04_tools_taxonomy.md` LOCKED decision (2026-05-27) to deliberately omit a
builder -- that ADR named its own reversal trigger verbatim: "add a 12-ISO
builder ONLY if an authoring flow (intent -> reverse_prompt) ever appears." The
2026-07-03 triage's evidence section does not cite that ADR, this KC's own prior
anti-pattern warning, or `kind_manifest_n00.md`'s "Emission (no builder)"
section -- flagged here for founder/orchestrator review before this reversal is
treated as settled. Until then: **the synthesizer remains canonical**. The
builder's scope is intentionally narrow (documentation / dry_run / repair /
calibration_pair only, per its bld_model Provenance Note) and it writes
exclusively to `records/pool/prompts/`, never to
`.cex/runtime/artifacts/reverse_prompts/`. `N00_genesis/P03_prompt/kind_index.md`
still carries the pre-builder "no builder" row and should be reconciled by a
future pass.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_prompt_template]] | upstream (the template the synthesizer fills) | 0.55 |
| [[p01_kc_rag_source]] | sibling (peer triangulation source -- contrast: consumed AS a source) | 0.38 |
| [[p01_kc_citation]] | related (provenance discipline for absorbed external sources) | 0.33 |
| [[p01_kc_prompt_compiler]] | related (resolves/fills the open_vars at Layer-1) | 0.30 |
| [[reverse-prompt-builder]] | related (narrow, non-canonical authoring path -- see Builder Note) | 0.35 |
