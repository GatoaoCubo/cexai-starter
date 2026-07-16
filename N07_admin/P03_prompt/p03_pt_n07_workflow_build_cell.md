---
id: p03_pt_n07_workflow_build_cell
kind: prompt_template
8f: F6_produce
pillar: P03
nucleus: n07
title: "Prompt Template -- N07 Workflow BUILD Cell"
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: n07_admin
domain: workflow-orchestration
quality: null
tags: [prompt_template, n07, workflow, build-cell, mode-w, grid]
tldr: "The BUILD-cell prompt contract N07 hands to a Sonnet subagent inside a Mode-W workflow: COMMON preamble (repo state + working discipline) + numbered implementation steps + a typed structured-return schema. Promoted from >=2x real usage across 14+ workflow scripts (R-167, anti-shelf rule)."
when_to_use: "Compose at F6 PRODUCE whenever N07 authors a .claude/workflows/*.js Mode-W script (grid.js family) that needs an agent() call implementing something. Fill the {{slots}}, do not paraphrase the shape."
primary_8f: PRODUCE
keywords: [workflow script, agent call, structured schema, COMMON preamble, Mode W, pytest_green, files_changed, ascii_clean]
density_score: 0.87
related:
  - p03_pt_n07_workflow_prove_cell
  - p03_pt_n07_workflow_fix_cell
  - p03_pt_n07_dispatch_handoff
---

# Prompt Template: N07 Workflow BUILD Cell

## Usage

Injected when N07 (or a workflow-authoring session acting as N07) writes a Mode-W
workflow script (`.claude/workflows/*.js`, the in-session Workflow tool grid family
-- see `.claude/rules/n07-orchestrator.md` "Mode W"). Every workflow script that has
implementation work to do opens with a BUILD phase shaped exactly like this template.
Fill the `{{slots}}`; do not invent a different shape per script -- the uniformity is
what lets a Fix/Prove/Verify cell downstream consume `build` predictably.

## Template

```
Build cell {{cell_id}}. {{COMMON}}
{{recon_context}}
IMPLEMENT: {{numbered_steps}}
TESTS: {{test_expectations}} Run {{test_command}} ({{baseline_note}}).
{{ascii_and_diff_discipline}}
Return structured.
```

Wrapper call (`agent(...)` signature actually used):

```js
let build = await agent(
  'Build cell {{cell_id}}. ' + COMMON + ' ' + '{{steps_prose}}',
  { label: '{{label}}', phase: 'Build', model: 'sonnet', effort: 'high', schema: BUILD }
)
```

## The COMMON preamble (repo-state + discipline, joined with spaces)

```js
const COMMON = [
  'Repo root (cwd): {{repo_root}}, branch {{branch}}, HEAD {{head_commit}} ({{tree_state}}).',
  '{{governing_contract_line}}',  // e.g. NUCLEUS ASSET CONTRACT / behavior-preserving-refactor warning / NEVER-FABRICATE clause
  'WORKING DISCIPLINE: read {{what_to_read_first}} before modifying; simplest structure first; ASCII-only .py; NEVER git commit/push; {{extra_constraints}}.',
].join(' ')
```

## The BUILD schema (typed structured-return contract)

```js
const BUILD = {
  type: 'object', additionalProperties: false,
  required: ['files_changed', '{{domain_specific_field}}', 'pytest_green', 'pytest_summary', 'ascii_clean', 'notes'],
  properties: {
    files_changed: { type: 'array', items: { type: 'string' } },
    {{domain_specific_field}}: { {{type_and_description}} },
    pytest_green: { type: 'boolean' }, pytest_summary: { type: 'string' },
    ascii_clean: { type: 'boolean' }, notes: { type: 'string' },
  },
}
```

## Variables

| Variable | Fills with | Source |
|----------|-----------|--------|
| {{cell_id}} | register row / mission slug (e.g. `R-164`, `R-148`) | mission plan |
| {{COMMON}} | the preamble block above | authored once per script, reused across Build/Fix/Prove |
| {{recon_context}} | prior Recon cell's JSON (if a Recon phase preceded Build) OR omitted | previous phase output |
| {{numbered_steps}} | (1)...(2)...(3)... concrete implementation steps, house-pattern citations first | task decomposition |
| {{test_expectations}} | what the new/existing tests must assert (house style: "absent field -> section omitted, sentinel never appears" etc.) | domain rules |
| {{test_command}} | usually `python -m pytest _tools/tests/ -k "{{marker}}" -q` | project test runner |
| {{baseline_note}} | prior green count, e.g. "baseline ~532+" -- lets the judge catch silent regressions | last known-good run |
| {{ascii_and_diff_discipline}} | "ASCII scan. Scoped diff." | `.claude/rules/ascii-code-rule.md` |
| {{domain_specific_field}} | one schema field unique to this cell's deliverable (e.g. `seams_migrated`, `cookbook_sections`, `kc_location_rationale`) | task-specific |

## Provenance (real usage, >=2x -- the anti-shelf gate for this promotion)

Cited from `.claude/projects/.../workflows/scripts/*.js` (last 24h, 2026-07-03 session):

| Script | Cell label | Domain field |
|--------|-----------|--------------|
| `r164-carry-registry-wf` | `build:registry` | `seams_migrated` |
| `r148-cookbook-at-emit-wf` | `build:cookbook` | `cookbook_sections` |
| `r156-self-kc-seed-wf` | `build:self-kc-emitter` | `kc_location_rationale` |
| `r002-r160r2-carry-gates-final-wf` | `build:*` | (carry-gate specific) |
| `s7-honesty-r007-wf` | `build:*` | (honesty-gate specific) |
| `spec1-brain-runnable-wf` | `build:*` | (runnable-spec specific) |
| `pm3v2-h-memory-wf` | `build:*` (nested, 2 rounds) | (H-memory specific) |
| `pm23-procedural-carry-loop-wf` | `build:*` | (carry-loop specific) |
| `grid-fusion-wf` | `build:*` | (fusion specific) |
| `nucleus-dossier-mission-wf` | `build:*` | (dossier specific) |
| `r157-r158-pm1-bugs-wf` | `build:*` | (bugfix specific) |
| `r163-judge-library-wf` | `build:*` | (judge-library specific) |
| `r166-r167-nac-promotions-wf` | `build:r166-triage`, `build:r167-prompt-seed` | (this very session -- the cell producing this file used this exact shape) |
| `r171-sibling-schemas-wf` | `build:*` | (schema-sibling specific) |
| `small-batch-r004-r155-r011-wf` | `build:*` | (multi-row batch) |

14+ independent scripts, 2026-07-02/03. This is not a synthetic derivation -- it is
the literal recurring shape, generalized only by replacing concrete values with
`{{slots}}` per the R-167 anti-shelf rule (promote from >=2x real usage, never
mass-generate).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_pt_n07_workflow_prove_cell]] | sibling | 0.55 |
| [[p03_pt_n07_workflow_fix_cell]] | sibling | 0.55 |
| [[p03_pt_n07_dispatch_handoff]] | related | 0.40 |
| p07_jc_spec_fidelity | downstream | 0.32 |
| dispatch-depth | related | 0.30 |
