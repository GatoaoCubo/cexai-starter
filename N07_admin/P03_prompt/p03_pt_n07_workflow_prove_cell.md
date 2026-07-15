---
id: p03_pt_n07_workflow_prove_cell
kind: prompt_template
8f: F6_produce
pillar: P03
nucleus: n07
title: "Prompt Template -- N07 Workflow PROVE Cell"
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: n07_admin
domain: workflow-orchestration
quality: null
tags: [prompt_template, n07, workflow, prove-cell, evidence, mode-w, grid]
tldr: "The PROVE/evidence-cell prompt contract: takes a BUILD cell's output, re-derives ground truth by RE-DOING the thing from scratch (fresh emit, live run, A/B snapshot) rather than trusting the build cell's self-report, and returns ok:boolean + concrete evidence fields. Promoted from >=2x real usage (6 scripts, R-167 anti-shelf rule)."
when_to_use: "Compose at F6 PRODUCE right after a BUILD (and any Fix round) inside a Mode-W workflow script, whenever the deliverable's correctness cannot be trusted from the build cell's own claims and needs independent re-derivation before a judge sees it."
primary_8f: PRODUCE
keywords: [evidence, fresh emit, A/B equivalence, operator-verbatim, refusal flip, ok boolean, independent re-derivation]
density_score: 0.87
related:
  - p03_pt_n07_workflow_build_cell
  - p03_pt_n07_workflow_fix_cell
  - p07_jc_spec_fidelity
  - verify
---

# Prompt Template: N07 Workflow PROVE Cell

## Usage

Injected right after a BUILD phase (and after each Fix round) in a Mode-W workflow
script, whenever a build cell's self-report ("pytest_green: true") is not sufficient
evidence on its own -- the PROVE cell independently RE-DERIVES the outcome (a fresh
distill emit, a live in-tenant 8F run, an A/B hash comparison) instead of re-reading
the build cell's claims. This is the workflow-level analogue of the `verify` skill's
"exercise the flow, don't just trust tests" principle.

## Template

```
PROVE cell {{cell_id}} (round {{round}}). {{COMMON}} Build: {{build_json}} .
STEPS: {{numbered_reproduction_steps}}
{{ok_gate_rule}}
Return structured.
```

Wrapper call (`agent(...)` signature actually used, inside a `while (blockers.length > 0 && round < 2)` loop):

```js
phase('Prove')
prove = await agent(
  'PROVE cell {{cell_id}} (round ' + round + '). ' + COMMON + ' Build: ' + JSON.stringify(build) + ' . ' +
  '{{steps_prose}}',
  { label: '{{label}}', phase: 'Prove', model: 'sonnet', schema: PROVE }
)
if (!prove.ok) { blockers = ['prove failed: ' + prove.notes]; judges = []; round++; continue }
```

## The PROVE schema (typed structured-return contract)

```js
const PROVE = {
  type: 'object', additionalProperties: false,
  required: ['ok', '{{primary_evidence_field}}', '{{secondary_evidence_field}}', 'notes'],
  properties: {
    ok: { type: 'boolean' },
    {{primary_evidence_field}}: { {{type_and_description}} },  // e.g. tree_diff, citation_sweep, refusal_flipped
    {{secondary_evidence_field}}: { {{type_and_description}} },
    notes: { type: 'string' },
  },
}
```

## Variables

| Variable | Fills with | Source |
|----------|-----------|--------|
| {{cell_id}} | register row / mission slug | mission plan |
| {{round}} | 0-indexed retry counter (`round`) | the enclosing while-loop |
| {{COMMON}} | same preamble block as the sibling BUILD cell (reused verbatim) | authored once per script |
| {{build_json}} | `JSON.stringify(build)` -- the BUILD cell's full structured output | previous phase output |
| {{numbered_reproduction_steps}} | concrete re-derivation steps: (1) delete+fresh-emit or re-run, (2) capture ground truth independently, (3) compare/sample, (4) state gate | domain rules |
| {{ok_gate_rule}} | the one-sentence rule for when `ok=true` is allowed (house style: "ok=true ONLY on full equivalence" / "refusal_flipped=true ONLY IF ...") | domain rules -- always explicit, never implicit |
| {{primary_evidence_field}} / {{secondary_evidence_field}} | schema fields unique to what is being proven (e.g. `tree_diff`+`ledger_diff`, `citation_sweep`+`operator_samples`, `refusal_flipped`+`f3_evidence`) | task-specific |

## Provenance (real usage, >=2x -- the anti-shelf gate for this promotion)

Cited from `.claude/projects/.../workflows/scripts/*.js` (last 24h, 2026-07-03 session)
-- 6 independent scripts carry an explicit `phase('Prove')` step:

| Script | Cell label | What it independently re-derives |
|--------|-----------|-----------------------------------|
| `r164-carry-registry-wf` | `prove:ab-r{round}` | A/B emit equivalence (hash-manifest of A-side snapshot BEFORE re-emit, then fresh B-side emit, then file-set + hash + ledger comparison) |
| `r148-cookbook-at-emit-wf` | `prove:operator-r{round}` | fresh emit + independent citation sweep + 3 operator-verbatim command runs |
| `r156-self-kc-seed-wf` | `prove:refusal-flip-r{round}` | fresh emit + literal in-tenant 8F run capturing the F3 injection log lines (the "refusal flip") |
| `r002-r160r2-carry-gates-final-wf` | `prove:*` | fresh emit + bleed-0 verification |
| `s7-honesty-r007-wf` | `prove:*` | fresh emit + declared-gate execution evidence |
| `pm3v2-h-memory-wf` | `prove:*` | H-memory read-back proof after write |

All 6 share the same discipline: the prove cell never trusts the build cell's
"pytest_green: true" as sufficient -- it re-runs the real thing (a fresh distill
emit, a live 8F call, a hash comparison) and only THEN reports `ok`. This is the
pattern being promoted -- generalized only by variable substitution, per the R-167
anti-shelf rule.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_pt_n07_workflow_build_cell]] | sibling | 0.55 |
| [[p03_pt_n07_workflow_fix_cell]] | sibling | 0.55 |
| p07_jc_spec_fidelity | downstream | 0.35 |
| verify | related | 0.32 |
