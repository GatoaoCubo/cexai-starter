---
quality: null
id: p11_fb_prompt_package
kind: builder_default
pillar: P11
title: "Feedback: Prompt Package"
domain: prompt_package
version: 1.0.0
tags: [feedback, anti-patterns, P11, prompt_package, decompose]
8f: "F7_govern"
keywords: [prompt package, never rules, failure modes, correction protocol, feedback, anti-patterns, prompt_package, dguard, wikilink gate]
tldr: "Anti-patterns and correction protocol for the prompt-package-builder. 6 NEVER rules + 4 real failure modes (DGUARD/wikilink-gate-grounded) + 4-step correction."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - p11_fb_prompt_template
  - bld_eval_prompt_package
  - bld_memory_prompt_package
  - p03_ins_prompt_package
  - prompt-package-builder
---
# Feedback: Prompt Package

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H08 |
| No live tools in body | Never embed an unresolved MCP/retrieval call in `## CONTEXT` | H06 |
| ASCII-only code | No emoji, no accented chars in any `.py`/`.ps1`/`.sh` this builder touches | H04 (repo-wide) |
| No partial handoff | All 4 body sections complete; no truncation, no "..." mid-section | H05 |
| No frontmatter omission | Every package starts with valid YAML frontmatter incl. `package_type` | H01, H02 |
| No unregistered target | `target_kind` MUST resolve in `.cex/kinds_meta.json` before Stage 1 writes the package | H03 |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Factual-synthesis kind decomposed unguarded | `target_kind` in `FACTUAL_SYNTHESIS_KINDS` (`knowledge_card`, `faq_entry`, `glossary_entry`, `mental_model`, `domain_vocabulary`) with `CEX_DECOMPOSE_GUARD` unset | Set `--guard-on-factual upgrade` (self-heals the tier) or route to `solo`/native Sonnet instead |
| Fabricated wikilinks in the produced artifact | Stage-3 W2 gate reports fabricated `links` | Default policy `reject` blocks F8 already; do not weaken to `drop` without a documented reason |
| Truncated `## TEMPLATE` embed | Embedded `bld_output` content cut mid-table (writer caps at 3000 chars) | Prefer the SHORTEST correct `bld_output` for the target kind, or split the handoff |
| Naming-pattern mismatch | Tooling globs `p03_pp_*.md` and finds nothing | Follow the REAL convention (`pp_{target_kind}_{id}.md`); flag the registry gap, do not silently invent a third pattern |

## Correction Protocol

| Step | Action | Gate |
|------|--------|------|
| 1 | Identify which H01-H08 gate failed (see `bld_eval_prompt_package.md`) | F7 |
| 2 | Return to Phase 1/3 of `p03_ins_prompt_package.md` with the explicit fix instruction | F6 |
| 3 | Re-run F7 GOVERN against the full HARD gate table | F7 |
| 4 | Max 2 retries before escalating to N07 orchestrator (per `.claude/rules/n07-orchestrator.md` timeout handling) | F8 |

## Key Behaviors

- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact
- Builder MUST run F7 GOVERN quality gate before handing off to Stage 2
- Builder MUST compile output via `cex_compile.py` after saving (F8 COLLABORATE)
- Builder MUST signal completion via `signal_writer.write_signal`, not a self-assigned score
- Builder MUST NOT self-score: `quality` field is always `null` in own output
- Builder MUST NOT let the produced package skip the Stage-3 W2 wikilink gate on the downstream artifact

## Quality Thresholds

| Dimension | Weight | Target | Gate |
|-----------|--------|--------|------|
| Structural completeness (8 fields + 4 sections) | 30% | >= 8.0 | L1 |
| Rubric compliance (`bld_eval_prompt_package.md`) | 30% | >= 8.0 | L2 |
| Semantic coherence (CONTEXT genuinely pre-resolved) | 40% | >= 8.5 | L3 |
| Density score | -- | >= 0.85 | S09 |
| Tables present | -- | >= 1 | S05 |

## Gate Check

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
python -m pytest _tools/tests/test_decompose_guard.py _tools/tests/test_8f_runner.py -q
```

```yaml
# Expected output structure
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 8/8
density: 0.85+
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_fb_prompt_template]] | sibling | 0.81 |
| bld_eval_prompt_package | sibling | 0.79 |
| [[bld_memory_prompt_package]] | sibling | 0.79 |
| [[p03_ins_prompt_package]] | sibling | 0.77 |
| [[prompt-package-builder]] | sibling | 0.75 |
