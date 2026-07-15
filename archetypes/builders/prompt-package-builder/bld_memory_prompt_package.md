---
kind: memory
id: bld_memory_prompt_package
pillar: P10
llm_function: INJECT
purpose: Accumulated production experience for prompt_package artifact generation
memory_scope: project
observation_types: [reference, project, feedback]
quality: null
title: "Memory Prompt Package"
version: "1.0.0"
author: builder
tags:
  - "prompt_package"
  - "builder"
  - "decompose"
tldr: "Real, measured lessons about Mode B decompose failure modes -- MISSION_BENCH's factual-synthesis finding and bench2's wikilink-fabrication finding, both cited from cex_decompose.py's own code."
domain: "prompt package construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F3_inject"
keywords:
  - "prompt package construction"
  - "mission_bench"
  - "dguard"
  - "wikilink gate"
  - "factual synthesis"
  - "decompose"
  - "cex_decompose.py"
density_score: 0.90
related:
  - bld_knowledge_card_prompt_package
  - prompt-package-builder
  - bld_orchestration_prompt_package
  - p03_ins_prompt_package
  - p01_kc_prompt_package
---
# Memory: prompt-package-builder

## Summary

A prompt_package's entire value proposition is that a cheap Stage-2 model can execute F6 PRODUCE
CORRECTLY with zero live tools and zero memory of Stage 1's reasoning. The critical production
insight, MEASURED not assumed: the cheap path is NOT uniformly capable. `MISSION_BENCH`
(2026-06-15, `p07_bm_mission_bench`) proved Mode B (topology C: Opus F1-F4 -> cheap Haiku F6 ->
tools) CONSISTENTLY FAILS T1 factual synthesis -- `knowledge_card` scored q=1.2 BOTH benchmark
rounds, 8.4x worse than the frontier path (native Sonnet D=17.75 / decompose+thin E=19.60). Root
cause, per `cex_decompose.py` line 469: "the cheap Stage-2 producer cannot SYNTHESIZE factual
prose from a prompt_package -- it can fill a schema/template (decompose's real value) but not
compose grounded factual content." This is the ROUTING PLAYBOOK's documented anti-pattern
("NEVER use C for T1", `kc_mission_token_routing`), now also enforced in code as DGUARD.

## Pattern

1. A prompt_package is strongest for schema/template-filling kinds (`enum_def`, `type_def`,
   `env_config`, `naming_rule`, `response_format`, `input_schema`, `validation_schema`,
   `event_schema`) -- `cex_router_v2.STRUCTURED_ALLOW`'s pure-structural subset
2. A prompt_package is WEAKEST for factual-prose kinds (`knowledge_card`, `faq_entry`,
   `glossary_entry`, `mental_model`, `domain_vocabulary`) -- `FACTUAL_SYNTHESIS_KINDS` in
   `cex_decompose.py` line 486-489
3. `## CONTEXT` must carry PRE-RESOLVED facts; a cheap model reading an unresolved MCP call
   cannot execute it -- it will either hallucinate a result or leave the slot empty
4. Test the harvested package against >= 1 real downstream Stage-2 run before treating the
   `## TEMPLATE` embedding logic as correct -- a silently-truncated `bld_output` embed (the real
   writer caps it at 3000 chars) can drop required sections
5. The freshly-produced ARTIFACT (not the package) is what gets wikilink-gated at Stage 3 --
   design the `## CONTEXT` wikilinks to reference only artifacts that ACTUALLY exist on disk

## Anti-Pattern

1. Routing a factual-synthesis kind through Mode B with `CEX_DECOMPOSE_GUARD` unset (OFF by
   default) -- `Task tool: dispatch solo n0X "create kc_x"` silently becomes a known-failing cheap-F6 run
   unless the guard is turned on (`warn`/`upgrade`/`refuse`)
2. Assuming the producer-rail (constitution excerpt embedded in every package) alone stops
   fabrication -- bench2 measured 3/3 rail-governed cheap producers still fabricated
   `wikilinks` (7/7 artifacts = 0 real id-declarations on disk); the RAIL TEXT is necessary
   but not sufficient, which is exactly why the W2 gate exists as a separate, mechanical check
   (`cex_decompose.py` lines 223-289) rather than relying on the embedded rules alone
3. Skipping the A3 escalation opt-in for a mission where quality actually matters -- a
   GATE-CLEAN artifact (passes H01-H08) can still score below the quality floor; A3 exists
   precisely because gate-clean and quality-floor-clean are NOT the same claim
4. Confusing `prompt_package` (P03, one-shot handoff) with `prompt_template` (P03, reusable mold)
   -- a package that gets manually re-used across multiple unrelated builds has drifted into
   template territory and should be promoted/refactored, not kept as a "package"
5. Treating the registered naming (`p03_pp_{{task_id}}.md`) as ground truth when writing new
   tooling against the pool -- the real convention (`pp_{target_kind}_{id}.md`) is what actually
   exists on disk; code that globs `p03_pp_*.md` will find ZERO real files

## Context

Prompt packages sit in the P03 prompt layer, at the seam between Stage 1 (THINK: F1-F4, Opus/
Sonnet) and Stage 2 (GENERATE: F6, any cheap model). They exist because a 1M-token context on a
premium model is expensive to hold open for pure F6 filling -- decomposing lets a cheap model do
the mechanical half while the expensive model's reasoning is captured ONCE and reused.

## Impact

MISSION_BENCH's numbers, taken at face value: routing T1 (factual synthesis) through decompose
costs an 8.4x quality penalty vs. the frontier path. Bench2's wikilink finding: an UNGATED cheap
producer fabricates links at a 100% rate in the sampled runs (3/3), which is why Stage 3's W2
gate is a HARD block (default `reject`), not an advisory. The DGUARD `upgrade` policy (bump one
escalation-ladder tier) is the self-healing default recommended for autoroute paths precisely
because `warn`-only policies do not change behavior, only visibility.

## Reproducibility

For a reliable prompt_package: (1) confirm the target kind is NOT in `FACTUAL_SYNTHESIS_KINDS`,
or explicitly accept/guard the risk if it is; (2) harvest F1-F4 state without truncation-induced
gaps (respect the real writer's per-section char budgets, note what got cut); (3) embed the
target kind's `bld_output` ISO verbatim, not a paraphrase; (4) validate against
`p06_if_prompt_package.md` before handoff; (5) let Stage 3's W2 gate + doctor + compile run
un-skipped; (6) re-run `python -m pytest _tools/tests/test_decompose_guard.py
_tools/tests/test_8f_runner.py -q` after any change to this builder's ISOs (57 passed, 8 skipped
as of this session -- the 8 skips are an environment condition, a gitignored lab-only builder
map, not a functional failure).

## References

1. `_tools/cex_decompose.py` lines 463-594 (DGUARD block, MISSION_BENCH citation, T1 numbers)
2. `_tools/cex_decompose.py` lines 223-289 (W2 wikilink gate, bench2 citation)
3. `_tools/cex_decompose.py` lines 336-460 (A3 quality-floor escalation)
4. `N00_genesis/P06_schema/p06_if_prompt_package.md` (bilateral Stage1/Stage2 contract)

## Metadata

```yaml
id: bld_memory_prompt_package
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-memory-prompt-package.md
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `memory` |
| Pillar | P10 |
| Domain | prompt package construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_prompt_package]] | upstream | 0.57 |
| [[prompt-package-builder]] | upstream | 0.55 |
| [[bld_orchestration_prompt_package]] | upstream | 0.47 |
| [[p03_ins_prompt_package]] | upstream | 0.46 |
| [[p01_kc_prompt_package]] | upstream | 0.45 |
