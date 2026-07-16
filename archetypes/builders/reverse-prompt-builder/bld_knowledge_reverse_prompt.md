---
kind: knowledge_card
id: bld_knowledge_card_reverse_prompt
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for reverse_prompt production -- atomic searchable facts
sources: reverse-prompt-builder MANIFEST.md + GitReverseSynthesizer + kc_reverse_prompt.md + adr_v04_tools_taxonomy.md
quality: null
title: "Knowledge Card Reverse Prompt"
version: "1.0.0"
author: n03_builder
tags: [reverse_prompt, builder, examples]
tldr: "Domain facts for reverse_prompt production: the canonical deterministic producer, this builder's narrow exception scope, and the boundary vs sibling P03 kinds."
domain: "reverse prompt construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F3_inject"
keywords: [reverse prompt construction, knowledge card reverse prompt, reverse_prompt, builder, examples, GitReverseSynthesizer, tree_sha, open_vars, license gate, equivalence rubric]
density_score: 0.90
related:
  - bld_memory_reverse_prompt
  - reverse-prompt-builder
---
# Domain Knowledge: reverse_prompt
## Executive Summary
A `reverse_prompt` is the FILLED, FROZEN instance produced when a repo synthesizer converts one public repo into a single reconstruction prompt calibrated by 3 open_vars. The CANONICAL producer is `cexai.tools.reposynth.synthesizer.GitReverseSynthesizer` (deterministic: temperature 0.0, sorted extraction, fixed template -- byte-identical for a given `(tree_sha, filled_vars)`). This builder is a documented EXCEPTION path (see the Provenance Note in `bld_model_reverse_prompt.md`) for hand-authored drafts -- it is never a substitute for a real synthesis.
## Spec Table
| Property | Value |
|----------|-------|
| Pillar | P03 |
| Kind | `reverse_prompt` (exact literal) |
| ID pattern | `p03_rp_{slug}` (kinds_meta naming: `p03_rp_{{name}}.md`) |
| Canonical runtime path | `.cex/runtime/artifacts/reverse_prompts/<tree_sha>.md` -- NOT this builder's output path |
| Builder output path | `records/pool/prompts/p03_rp_{slug}.md` |
| depends_on | `prompt_template` (the fixed synthesis template it fills) |
| Max body | 8192 bytes |
| Quality field | always `null` |
| Open vars | target_audience (str) / target_runtime (enum, rebind_allowed:false) / complexity_level (enum, rebind_allowed:true) |
| Determinism | byte-identical for real synthesizer runs ONLY (temp 0.0); NOT guaranteed for this builder's hand-authored output |
| License gate | fail-closed BEFORE any LLM call (Article XVII); `LicenseCompatibilityError` aborts, `LicenseUnknownWarning` marks `derived_from_unlicensed_source` |
## Patterns
| Pattern | Application |
|---------|-------------|
| Triangulation source | 4th auto-research source (US P2); `synthesize_for_triangulation()` returns a `TriangulationBriefFragment` with a completeness-derived confidence |
| Rebind vs re-synthesize | Same repo + new `target_audience`/`complexity_level` = rebind; new `target_runtime` = fresh synthesis (FR-014) |
| Equivalence, not identity | Cross-runtime outputs judged EQUIVALENT (5-criteria C1-C5) not byte-identical -- `rubric_reverse_prompt_equivalence.md` |
| Fail-closed legal hygiene | Incompatible upstream LICENSE aborts before spend; no-LICENSE marks the artifact, does not block |
| Lean-registration precedent | `approval_request` (v0.3-W3b, `adr_v03_governance_taxonomy.md`) got the SAME "no builder, runtime-emitted" treatment -- this is a repeated architectural pattern, not unique to this kind |
## Anti-Patterns
| Anti-Pattern | Why it fails |
|-------------|-------------|
| Authoring a "real" reconstruction via this builder | Determinism (a FAIL criterion in `kc_reverse_prompt.md`) is a synthesizer guarantee this builder cannot make |
| Writing builder output into `.cex/runtime/artifacts/reverse_prompts/` | That path is reserved for the deterministic tool; collision risks corrupting the tree_sha cache-key semantics |
| Treating it as a `prompt_template` | Template = reusable unfilled mold; reverse_prompt = one filled, frozen instance |
| Treating it as a `knowledge_card` | KC = factual note; reverse_prompt = generative reconstruction prompt |
| Omitting license disclosure | Article XVII is fail-closed; silence is not neutral -- state `upstream_license` or `derived_from_unlicensed_source` |
## Application
1. Confirm mode (document/dry_run/repair/calibration_pair) -- NEVER "live synthesis substitute"
2. Resolve + validate all 3 open_vars (enum checks per `GitReverseSynthesizer._resolve_vars`)
3. Disclose provenance + license status explicitly in the body
4. Write to the builder pool path, never the synthesizer's runtime path
5. Validate H01-H10 (`bld_eval_reverse_prompt.md`) before delivery
## References
- `cexai/cexai/tools/reposynth/synthesizer.py` (GitReverseSynthesizer, 463 lines, 29/29 tests passing)
- `cexai/cexai/tools/reposynth/license_gate.py` (SPDX compatibility matrix)
- `N00_genesis/P01_knowledge/library/kind/kc_reverse_prompt.md` (kind KC)
- `cexai/docs/adr_v04_tools_taxonomy.md` (LOCKED lean-registration ADR)
- `cexai-specs/_revisions/rubric_reverse_prompt_equivalence.md` (equivalence rubric)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_reverse_prompt]] | downstream | 0.57 |
| [[reverse-prompt-builder]] | downstream | 0.55 |
