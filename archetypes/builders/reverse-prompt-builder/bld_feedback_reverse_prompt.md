---
quality: null
id: p11_fb_reverse_prompt
kind: builder_default
pillar: P11
title: "Feedback: Reverse Prompt"
domain: reverse_prompt
version: 1.0.0
tags: [feedback, anti-patterns, P11, reverse_prompt]
8f: "F7_govern"
keywords: [reverse prompt, never rules, failure modes, step correction, feedback, anti-patterns, reverse_prompt, common failure modes, failure mode, correction protocol]
tldr: "Anti-patterns and correction protocol for reverse-prompt-builder. 6 NEVER rules + 4 failure modes + 3-step correction, centered on provenance honesty."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - p11_qg_reverse_prompt
  - reverse-prompt-builder
  - bld_memory_reverse_prompt
  - p03_ins_reverse_prompt
  - bld_collaboration_reverse_prompt
---
# Feedback: Reverse Prompt

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign a quality score to own output | H04 |
| No hallucination | Cite `source_url` / `tree_sha`; never invent repo content | H07 |
| No determinism claim | Never claim byte-determinism for a hand-authored draft | H09 |
| No path collision | Never write to `.cex/runtime/artifacts/reverse_prompts/` | H10 |
| No license silence | Always disclose `upstream_license` or `derived_from_unlicensed_source` | H08 |
| No live-synthesis substitution | Never hand-author a draft as a stand-in for a REAL synthesis request | -- |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Provenance omitted | No `## Provenance` section | Add mode + determinism disclosure (Phase 3) |
| Open-var drift | 4th var invented, or an enum value outside the valid set | Re-check `_VALID_RUNTIMES` / `_VALID_COMPLEXITY` |
| Boundary confusion | Reads like a reusable `{{var}}` template | Route to prompt-template-builder instead |
| Missing license note | `source_url` present, no license field | Add `upstream_license` or `derived_from_unlicensed_source: true` |

## Correction Protocol

| Step | Action | Gate |
|------|--------|------|
| 1 | Identify which H01-H10 gate failed | F7 |
| 2 | Return to F6 PRODUCE with an explicit fix instruction | F6 |
| 3 | Re-run F7 GOVERN | F7 |
| 4 | Max 2 retries before escalating to N07 | F8 |

## Key Behaviors

- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact
- Builder MUST run F7 GOVERN (H01-H10) before saving output
- Builder MUST compile output via `cex_compile.py` after saving (F8 COLLABORATE)
- Builder MUST signal completion with a quality score to the N07 orchestrator
- Builder MUST NOT self-score: `quality` field is always null in its own output
- Builder MUST route REAL synthesis requests to `cexai repo_synthesizer create <url>`, never hand-author a substitute

## Quality Thresholds

| Dimension | Weight | Target | Gate |
|-----------|--------|--------|------|
| Structural completeness (H01-H10) | 30% | >= 8.0 | L1 |
| Rubric compliance (C1-C5, when applicable) | 30% | >= 8.0 | L2 |
| Provenance honesty | 40% | >= 8.5 | L3 |
| Density score | -- | >= 0.80 | S09 |
| Tables present | -- | >= 1 | S05 |

## Gate Check

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
```

```yaml
# Expected output structure
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 10/10
density: 0.85+
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_reverse_prompt]] | sibling | 0.81 |
| [[reverse-prompt-builder]] | upstream | 0.79 |
| [[bld_memory_reverse_prompt]] | sibling | 0.79 |
| [[p03_ins_reverse_prompt]] | sibling | 0.79 |
| [[bld_collaboration_reverse_prompt]] | sibling | 0.77 |
