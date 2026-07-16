---
kind: architecture
id: bld_architecture_reverse_prompt
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of reverse_prompt -- inventory, dependencies, and architectural position
quality: null
title: "Architecture Reverse Prompt"
version: "1.0.0"
author: n03_builder
tags: [reverse_prompt, builder, examples]
tldr: "Component inventory grounded in the REAL GitReverseSynthesizer internals, plus this builder's narrow, non-canonical position relative to it."
domain: "reverse prompt construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [component map of reverse_prompt, architecture reverse prompt, reverse_prompt, builder, examples, GitReverseSynthesizer, license_gate, dependency graph, boundary table, canonical]
density_score: 0.90
related:
  - reverse-prompt-builder
  - bld_memory_reverse_prompt
---
# Architecture: reverse_prompt in the CEX
## Component Inventory (REAL, from GitReverseSynthesizer)
| Name | Role | Owner | Status |
|------|------|-------|--------|
| `GitReverseSynthesizer.extract` | Normalizes repo_url, calls the injected RepoSource, sorts+truncates the tree (5000-path budget), caps entry files (10) | synthesizer.py | active (canonical) |
| `GitReverseSynthesizer._project` | License gate -> `_synthesize_body` -> `_build_frontmatter` -> `_write_artifact` | synthesizer.py | active (canonical) |
| `_resolve_vars` | Fills + validates the 3 open_vars against the enum sets | synthesizer.py | active (canonical) |
| `_synthesize_body` | Dispatches `cexai.foundation.llm.call` at temperature 0.0 with the fixed `_SYSTEM_PROMPT` | synthesizer.py | active (canonical) |
| `license_gate.check_license_compatibility` | SPDX rank matrix; fail-closed before LLM spend | license_gate.py | active (canonical) |
| reverse-prompt-builder (this scaffold) | Hand-authors documentation / dry-run / repair / calibration drafts | this builder | active (non-canonical, narrow) |
## Dependency Graph
```
prompt_template --filled_by--> GitReverseSynthesizer --emits--> reverse_prompt (canonical, .cex/runtime/artifacts/)
prompt_template --documented_by--> reverse-prompt-builder --drafts--> reverse_prompt (pool, non-canonical)
reverse_prompt --triangulates--> auto-research Layer-1 context (4th source, US P2)
reverse_prompt --judged_by--> rubric_reverse_prompt_equivalence (C1-C5)
```
| From | To | Type | Data |
|------|----|------|------|
| prompt_template (P03) | reverse_prompt | fills | fixed synthesis template + RepoExtract + open_vars |
| GitReverseSynthesizer (P04 tool) | reverse_prompt | emits | canonical, byte-deterministic instance |
| reverse-prompt-builder (this) | reverse_prompt | drafts | non-canonical documentation/dry-run/repair instance |
| reverse_prompt | triangulation brief (P01) | feeds | 4th auto-research source, completeness-scored |
| reverse_prompt | rubric_reverse_prompt_equivalence (P07) | judged_by | C1-C5 cross-runtime equivalence |
| license_gate (P04) | reverse_prompt | gates | fail-closed before LLM spend (canonical path only) |
## Boundary Table
| reverse_prompt IS | reverse_prompt IS NOT |
|--------------------|------------------------|
| A filled, frozen INSTANCE from one repo | A reusable `{{variable}}` MOLD (that's `prompt_template`) |
| Byte-deterministic when synthesizer-emitted | Byte-deterministic when hand-authored by this builder |
| A generative reconstruction PROMPT | A factual note (`knowledge_card`) |
| Cached/keyed by `tree_sha` | Named/keyed by an arbitrary slug at the file-path level |
| Emitted primarily by `GitReverseSynthesizer` | Primarily builder-authored (this scaffold is the narrow exception) |
## Layer Map
| Layer | Components | Purpose |
|-------|------------|---------|
| Template | prompt_template | Fixed synthesis mold |
| Extraction | RepoExtract, RepoSource | Sorted file tree + README + entry files |
| Synthesis | GitReverseSynthesizer, license_gate, foundation.llm | Canonical deterministic path |
| Authoring (narrow) | reverse-prompt-builder (this) | Documentation / dry-run / repair / calibration only |
| Consumption | downstream LLM reconstruction, auto-research triangulator | Real + research uses |
| Judgment | rubric_reverse_prompt_equivalence | Cross-runtime equivalence scoring |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[reverse-prompt-builder]] | upstream | 0.53 |
| [[bld_memory_reverse_prompt]] | downstream | 0.49 |
