---
kind: memory
id: bld_memory_reverse_prompt
pillar: P10
llm_function: INJECT
purpose: Accumulated production experience for reverse_prompt artifact generation
memory_scope: project
observation_types: [user, feedback, project, reference]
quality: null
title: "Memory Reverse Prompt"
version: "1.0.0"
author: n03_builder
tags:
  - "reverse_prompt"
  - "builder"
  - "examples"
tldr: "This kind has a real, deterministic 5-week-older producer and a LOCKED ADR that declined a builder for it -- the critical lesson is scope discipline, not authoring dominance."
domain: "reverse prompt construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F3_inject"
keywords:
  - "reverse prompt construction"
  - "memory reverse prompt"
  - "reverse_prompt"
  - "builder"
  - "examples"
  - "GitReverseSynthesizer"
  - "locked ADR"
  - "provenance"
  - "scope discipline"
density_score: 0.90
related:
  - reverse-prompt-builder
---
# Memory: reverse-prompt-builder
## Summary
`reverse_prompt` is architecturally unusual among P03 kinds: it has a REAL, working, deterministic, 29-test-covered producer (`GitReverseSynthesizer`) that predates this builder by 5+ weeks (2026-05-27 vs 2026-07-03), and a LOCKED ADR (`adr_v04_tools_taxonomy.md`) that explicitly declined to scaffold a builder for exactly this reason. The critical production insight is that this builder does NOT close the same gap most 12-ISO builders close (human/LLM intent with no existing production path) -- it closes a NARROWER gap: intent-resolution routing (F2 BECOME had no target for a free-form "build me a reverse_prompt" request). Treating this builder as the primary producer would be a regression, not an improvement.
## Pattern
1. Always check whether a request is for a REAL synthesis first -- route to `cexai repo_synthesizer create <url>`, never hand-author a substitute
2. Every hand-authored draft discloses `mode` and non-determinism explicitly in `## Provenance`
3. Never write drafts into the synthesizer's reserved runtime path (`tree_sha` is a cache key, not decoration)
4. The 3 open_vars are FIXED (never add a 4th) -- `target_runtime` never rebinds in place
5. License disclosure is not optional even in hand-authored drafts -- mirror Article XVII's fail-closed spirit
6. When two instances of the same repo need comparing, use the C1-C5 equivalence rubric, not a byte-diff
## Anti-Pattern
1. Presenting a builder-authored draft as if it were synthesizer output -- breaks the kind's own FAIL criterion (non-determinism)
2. "Fixing" `.cex/runtime/artifacts/reverse_prompts/<tree_sha>.md` filenames to match `p03_rp_` naming -- destroys the cache key
3. Silently ignoring the LOCKED `adr_v04_tools_taxonomy.md` re-evaluation trigger ("add a builder ONLY if an authoring flow appears") -- this scaffold IS acting on that trigger; say so explicitly, do not hide it
4. Adding a 4th open_var or renaming the fixed 3 -- breaks `_resolve_vars` enum validation parity
5. Confusing `reverse_prompt` (filled instance) with `prompt_template` (its own upstream mold)
## Context
`reverse_prompt` sits in P03 alongside `prompt_template` (its sole `depends_on`) and `chain` (nearest functional sibling per the ADR's reuse-candidate table, also P03/PRODUCE/F6_produce). Unlike most P03 kinds, its primary producer is a deterministic tool, not an LLM builder -- this builder is deliberately secondary. `approval_request` (v0.3-W3b, `adr_v03_governance_taxonomy.md`) received the identical "lean, no builder" treatment, then was ALSO scaffolded in this same 2026-07-03 wave -- this is a repeated pattern across the batch, not unique to this kind.
## Impact
Not yet measured in production (this scaffold is 2026-07-03, day one). The rubric pilot (30-pair, kappa target 0.70) is the nearest quantified quality signal for the kind; no builder-specific quality history exists yet.
## Reproducibility
For any hand-authored draft: (1) confirm mode, (2) resolve+validate open_vars, (3) disclose provenance + license, (4) write to the pool path only, (5) validate H01-H10.
## References
1. `cexai/cexai/tools/reposynth/synthesizer.py` (canonical producer, 463 lines, 29/29 tests)
2. `cexai/docs/adr_v04_tools_taxonomy.md` (LOCKED lean-registration ADR)
3. `docs/DECISION_BUILDERLESS_KINDS_2026_07_03.md` (this scaffold's mandate)

## Metadata
```yaml
id: bld_memory_reverse_prompt
pipeline: 8F
scoring: hybrid_3_layer
```
```bash
python _tools/cex_score.py --apply bld-memory-reverse-prompt.md
```
## Properties
| Property | Value |
|----------|-------|
| Kind | `memory` |
| Pillar | P10 |
| Domain | reverse prompt construction |
| Pipeline | 8F (F1-F8) |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[reverse-prompt-builder]] | upstream | 0.55 |
