---
id: p03_pt_n07_workflow_fix_cell
kind: prompt_template
8f: F6_produce
pillar: P03
nucleus: n07
title: "Prompt Template -- N07 Workflow FIX Cell"
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: n07_admin
domain: workflow-orchestration
quality: null
tags: [prompt_template, n07, workflow, fix-cell, retry-loop, mode-w, grid]
tldr: "The FIX-round prompt contract: fires only when a judge/prove cell returned blockers, receives the blockers + evidence + prior build as context, root-causes in place (never patches over), and is bounded to a small fixed number of rounds inside a while(blockers.length>0 && round<N) loop. Promoted from >=2x real usage (10+ scripts, R-167 anti-shelf rule)."
when_to_use: "Compose at F6 PRODUCE inside a Mode-W workflow script's retry loop, the round AFTER a Prove/Verify cell reports blockers != []. Never invoked speculatively -- only in reaction to a concrete blocker list."
primary_8f: PRODUCE
keywords: [blockers, root-cause, bounded retry, round counter, while loop, judge evidence]
density_score: 0.86
related:
  - p03_pt_n07_workflow_build_cell
  - p03_pt_n07_workflow_prove_cell
  - p07_jc_spec_fidelity
---

# Prompt Template: N07 Workflow FIX Cell

## Usage

Injected as the reactive branch of a Mode-W workflow's retry loop -- it fires ONLY
when the prior Prove/Verify cell(s) returned a non-empty `blockers` array. It never
runs speculatively (there is no "fix in advance"). It receives the full evidence
trail (blockers + judge verdicts + the prior build) so it root-causes instead of
guessing, and the loop it lives in is always bounded (house convention: `round < 2`,
i.e. at most one fix attempt per prove/verify failure) so a stuck cell cannot spin
forever.

## Template

```
FIX cell {{cell_id}} round {{round}}: {{blockers_json}} Evidence: {{judges_json}} Build: {{build_json}} . {{COMMON}} {{fix_discipline}} Return structured.
```

Wrapper call (`agent(...)` signature actually used, as the first statement inside the retry loop body):

```js
let round = 0, prove = null, judges = [], blockers = ['first']
while (blockers.length > 0 && round < {{max_rounds}}) {
  if (round > 0) {
    phase('Fix')
    const fix = await agent(
      'FIX cell {{cell_id}} round ' + round + ': ' + JSON.stringify(blockers) +
      ' Evidence: ' + JSON.stringify(judges) + ' Build: ' + JSON.stringify(build) + ' . ' +
      COMMON + ' {{fix_discipline}} Return structured.',
      { label: 'fix:r' + round, phase: 'Fix', model: 'sonnet', effort: 'high', schema: BUILD }
    )
    if (fix && fix.files_changed) build = fix
  }
  // ... Prove / Verify happen after this block, re-populating `blockers` ...
  round++
}
```

Note the FIX cell reuses the **same schema as BUILD** (`schema: BUILD`) -- a fix is
a build with extra context, not a new artifact type. This is deliberate and appears
in every cited script.

## Variables

| Variable | Fills with | Source |
|----------|-----------|--------|
| {{cell_id}} | register row / mission slug (same as the sibling Build/Prove cells) | mission plan |
| {{round}} | 1-indexed retry counter at fire time (fix never fires at round 0) | the enclosing while-loop |
| {{blockers_json}} | `JSON.stringify(blockers)` -- flat array of blocker strings from the last judge/prove round | prior Prove/Verify output |
| {{judges_json}} | `JSON.stringify(judges)` -- full verdict objects (judge/verdict/blockers/warnings/evidence), not just the flat list, so the fix cell sees WHY | prior Verify output |
| {{build_json}} | `JSON.stringify(build)` -- the artifact state being fixed | prior Build/Fix output |
| {{COMMON}} | same preamble block as the sibling Build/Prove cells (reused verbatim) | authored once per script |
| {{fix_discipline}} | one-line root-cause instruction, house-style variants: "Root-cause, existing tests unmodified-green, return structured." / "Root-cause fix in Central only, scoped pytest green, return structured." / "Fix in the deliverable files only." | domain-specific, but always: root-cause (not patch-over) + a green-check + a scope boundary |
| {{max_rounds}} | bounded loop ceiling, house convention `2` (i.e. at most 1 fix attempt) | orchestration budget discipline |

## Provenance (real usage, >=2x -- the anti-shelf gate for this promotion)

Cited from `.claude/projects/.../workflows/scripts/*.js` (last 24h, 2026-07-03 session)
-- 10+ independent scripts carry this exact `while(blockers... && round<N) { if(round>0){phase('Fix')...} }` shape:

| Script | Loop ceiling | fix_discipline variant |
|--------|-------------|------------------------|
| `r164-carry-registry-wf` | `round < 2` | "Root-cause, existing tests unmodified-green, return structured." |
| `r148-cookbook-at-emit-wf` | `round < 2` | "Root-cause in Central, pytest green, return structured." |
| `r156-self-kc-seed-wf` | `round < 2` | "Root-cause fix in Central only, scoped pytest green, return structured." |
| `r002-r160r2-carry-gates-final-wf` | `round < 2` | (carry-gate specific) |
| `s7-honesty-r007-wf` | `round < 2` | (honesty-gate specific) |
| `spec1-brain-runnable-wf` | `round < 2` | (runnable-spec specific) |
| `grid-fusion-wf` | single fix (no loop counter) | "Fix in the deliverable files only." |
| `nucleus-dossier-mission-wf` | single fix (no loop counter) | (dossier specific) |
| `pm23-procedural-carry-loop-wf` | `round < 2` | (carry-loop specific) |
| `small-batch-r004-r155-r011-wf` | single fix (no loop counter) | (multi-row batch) |
| `r166-r167-nac-promotions-wf` | single fix (no loop counter) | (this very session -- the cell producing this file used the single-fix variant) |

Two sub-variants exist in the real corpus: the bounded `while` loop (Build/Fix/Prove/
Verify all in one cell, used for higher-risk regression-class work) and the simpler
single-fix-after-Verify shape (used for lower-risk parallel Build+Verify scripts).
Both are captured here because both recur >=2x; the loop-ceiling variable makes the
choice a slot, not a fork.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_pt_n07_workflow_build_cell]] | sibling | 0.55 |
| [[p03_pt_n07_workflow_prove_cell]] | sibling | 0.55 |
| p07_jc_spec_fidelity | downstream | 0.30 |
