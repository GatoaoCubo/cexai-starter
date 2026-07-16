---
id: p03_ins_reverse_prompt
kind: instruction
pillar: P03
version: 1.0.0
created: '2026-07-03'
updated: '2026-07-03'
author: instruction-builder
title: Reverse Prompt Builder Instructions
target: "reverse-prompt-builder agent"
phases_count: 4
prerequisites:
  - "Caller confirms this is NOT a request for a live repo reconstruction (that routes to cexai repo_synthesizer create <url>)"
  - "A mode is selected: document, dry_run, repair, or calibration_pair"
  - "source_url and the 3 open_vars (target_audience, target_runtime, complexity_level) are known or resolvable"
validation_method: checklist
domain: reverse_prompt
quality: null
tags: [instruction, reverse-prompt, P03, provenance, non-canonical]
idempotent: false
atomic: false
rollback: "Delete the produced .md draft under records/pool/prompts/. Never touches .cex/runtime/artifacts/reverse_prompts/ (out of scope), so no interference with synthesizer cache state."
dependencies: []
logging: true
tldr: "Confirm provenance mode, classify boundary vs sibling kinds, compose the artifact honoring open_vars + license disclosure, then validate H01-H10."
8f: "F6_produce"
keywords: [reverse prompt builder instructions, provenance mode, boundary check, open_vars, license disclosure, hard gates, instruction, reverse-prompt, non-canonical]
density_score: 0.91
llm_function: REASON
related:
  - reverse-prompt-builder
  - bld_memory_reverse_prompt
---
## Context
A `reverse_prompt` is the FILLED, FROZEN instance a repo synthesizer emits when it converts one public repo into a reconstruction prompt (see `kc_reverse_prompt.md`). This builder is a NARROW, non-canonical path -- real syntheses run through `GitReverseSynthesizer` / `cexai repo_synthesizer create <url>`, never here. See `bld_model_reverse_prompt.md`'s Provenance Note for the full grounding (a LOCKED ADR originally omitted this builder; a later triage scaffolded it to close an intent-resolution dead end).
**Inputs**
| Field | Type | Description |
|---|---|---|
| `mode` | enum | `document` \| `dry_run` \| `repair` \| `calibration_pair` -- see Phase 1 |
| `source_url` | string | Canonical repo reference (`<owner>/<repo>` or full https URL) |
| `target_audience` | string | Open var 1 (free text) |
| `target_runtime` | enum | `claude-code` \| `codex` \| `gemini` \| `ollama` |
| `complexity_level` | enum | `introductory` \| `intermediate` \| `advanced` |
| `known_tree_sha` | string, optional | If repairing/documenting a REAL synthesizer output, its tree_sha |
**Output**
A single `.md` file at `records/pool/prompts/p03_rp_{{slug}}.md` conforming to `bld_schema_reverse_prompt.md` + `bld_output_template_reverse_prompt.md`. Frontmatter + 6 body sections: Purpose, Provenance, Repo Extract Summary, Open Vars Table, Reconstruction Prompt Body, Quality Gates, Examples.
**Boundary rules**
- If the caller wants a REAL repo reconstructed right now -> decline and route to `cexai repo_synthesizer create <url>`. Do NOT hand-author a substitute.
- If the input has no named repo and is a reusable `{{variable}}` mold invoked many times -> that is `prompt_template` (the upstream this kind's `depends_on` points to), not `reverse_prompt`.
- If the input is a factual claim about a repo, not a reconstruction prompt -> `knowledge_card`, not `reverse_prompt`.
## Phases
### Phase 1: Determine Provenance (mode select)
```
IF caller wants a REAL repo synthesized right now:
  RETURN "Route to `cexai repo_synthesizer create <url>` -- this builder does
  not perform live synthesis."
mode <- ONE of:
  document         : hand-write an example/teaching instance (mirrors
                      kind_manifest_n00.md's own worked example)
  dry_run          : draft a calibrated body when synthesizer/network/LLM
                      is unavailable
  repair           : patch a real synthesizer-emitted artifact (preserve its
                      source_url/tree_sha verbatim)
  calibration_pair : produce a deliberately-varied second instance for
                      rubric_reverse_prompt_equivalence.md judge piloting
IF mode == repair:
  REQUIRE known_tree_sha; keep the original frontmatter untouched except the
  specific patched field
ELSE:
  REQUIRE an explicit "## Provenance" disclosure (Phase 3) marking this
  NOT byte-deterministic
```
### Phase 2: Classify -- Boundary Check
```
IF input has {{variable}} slots reused across MANY invocations:
  RETURN "This is a prompt_template -- route to prompt-template-builder."
IF input is a factual claim, not a generative reconstruction prompt:
  RETURN "This is a knowledge_card -- route to knowledge-card-builder."
IF input is a multi-step PROMPT SEQUENCE, not one repo -> one prompt:
  RETURN "This is a chain -- structural mismatch (nearest functional
  sibling per the ADR, not the same kind)."
IF input names ONE public repo AND produces ONE filled reconstruction prompt:
  PROCEED as reverse_prompt
```
### Phase 3: Compose -- Build the Artifact
```
ID generation:
  id = "p03_rp_" + owner_repo_slug (+ "_" + tree_sha[:7] if known)
  pattern must match: ^p03_rp_[a-z][a-z0-9_]+$
Frontmatter (bld_schema_reverse_prompt.md is the source of truth):
  id, kind (=reverse_prompt), pillar (=P03), title, version, created, updated,
  author, source_url, tree_sha (or an explicit non-sha marker for
  dry_run/calibration_pair), open_vars (fixed 3-tuple), filled_vars (map),
  quality (=null), tags, tldr, keywords, density_score
Body sections (in this order):
  ## Purpose            - one paragraph: what repo, why this instance exists
  ## Provenance          - mode; explicit "NOT byte-deterministic" unless
                          mode==repair preserving a real tree_sha; license
                          status (upstream_license OR
                          derived_from_unlicensed_source)
  ## Repo Extract Summary - primary_language, description, file_tree excerpt,
                          entry files referenced, truncated?
  ## Open Vars Table      - target_audience | target_runtime |
                          complexity_level + resolved values
  ## Reconstruction Prompt Body - fenced block, the actual instructions a
                          downstream LLM would receive
  ## Quality Gates        - H01-H10 status + notes
  ## Examples             - at least 1 filled example (variables + rendered
                          excerpt)
```
### Phase 4: Validate -- Gate Check
```
HARD gates (all must pass -- fix before delivering):
  H01: frontmatter parses as valid YAML
  H02: id matches ^p03_rp_[a-z][a-z0-9_]+$
  H03: kind == "reverse_prompt" (never overridden)
  H04: quality is null
  H05: all 3 open_vars declared with resolved filled_vars
  H06: target_runtime in {claude-code,codex,gemini,ollama}; complexity_level
       in {introductory,intermediate,advanced}
  H07: source_url present, normalized (https://{github|gitlab|bitbucket}.com/
       <owner>/<repo>)
  H08: license disclosed (upstream_license OR
       derived_from_unlicensed_source: true)
  H09: "## Provenance" section present AND non-determinism disclosed unless
       mode==repair
  H10: file size <= 8192 bytes; never written under
       .cex/runtime/artifacts/reverse_prompts/
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[reverse-prompt-builder]] | related | 0.48 |
| [[bld_memory_reverse_prompt]] | downstream | 0.39 |
