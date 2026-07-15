---
id: p03_pt_n07_dispatch_handoff
kind: prompt_template
8f: F6_produce
pillar: P03
nucleus: n07
title: "Prompt Template -- N07 Canonical Dispatch Handoff"
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: n07_admin
domain: dispatch-composition
quality: null
tags: [prompt_template, n07, handoff, dispatch, dispatch-depth, gdp]
tldr: "The canonical shape N07 fills to COMPOSE a handoff file before it becomes a real handoff artifact (kind=handoff, p12_ho_*.md) at .cex/runtime/handoffs/{mission}_{nucleus}.md. Frontmatter + Context + DECISIONS + Relevant artifacts + Expected output + Gates + optional ACR Prerequisites. Promoted from every-session real usage (dispatch-depth.md contract + N archived handoff instances), not synthetic."
when_to_use: "Compose at F6 PRODUCE whenever N07 is about to write .cex/runtime/handoffs/{mission}_{nucleus}.md before any solo/grid/decompose dispatch. Fill the {{slots}}; this is the FORM the handoff instance is rendered from, not the instance itself."
primary_8f: PRODUCE
keywords: [handoff, dispatch, Context pre-loaded, Relevant artifacts, Expected output, DECISIONS, ACR Prerequisites, dispatch-depth]
density_score: 0.86
related:
  - p03_pt_n07_workflow_build_cell
  - dispatch-depth
  - guided-decisions
  - n07-orchestrator
---

# Prompt Template: N07 Canonical Dispatch Handoff

## Kind decision (why `prompt_template`, not `action_prompt`)

R-167 asked for `p03_at_n07_dispatch_handoff.md` (action_prompt) or "the closest
right kind -- decide from kinds_meta and say why." Checked `.cex/kinds_meta.json`:

| Candidate | Boundary (from kinds_meta) | Fit |
|-----------|----------------------------|-----|
| `action_prompt` | "Specific task. The LLM EXECUTES this." naming `p03_up_{{task}}.md`, max 2048B | NO -- this artifact is not itself a task an LLM executes; it is a form used to COMPOSE tasks. 2048B is also too small for the full 6-section contract below. |
| `handoff` (P12) | "Handoff instruction (task + context + commit)", naming `p12_ho_{{task}}.md` | NO for THIS artifact's location -- `handoff` is the correct kind for the rendered INSTANCE (an actual `.cex/runtime/handoffs/{mission}_{nucleus}.md` file), but R-167 asked for the reusable template to live in `N07_admin/P03_prompt/`, and P12 is the wrong pillar for a P03 prompt-set deliverable. |
| `prompt_template` | "Template with variables ... NOT user_prompt (fixed) nor system_prompt (identity)", naming `p03_pt_{{topic}}.md`, max 8192B | YES -- this is exactly a reusable template with `{{slots}}` that N07 fills every time it composes a handoff. The 8192B ceiling fits the full contract. |

Decision: `kind: prompt_template`, filed as `p03_pt_n07_dispatch_handoff.md`
(not `p03_at_...`). Every rendered instance of this template still becomes a
`kind: handoff` artifact once written to `.cex/runtime/handoffs/`.

## Usage

Fill this template at F6 PRODUCE, immediately before `the Task tool (in-session)
solo|grid|decompose`, per `.claude/rules/dispatch-depth.md` (mandatory: at least
3 depth amplifiers) and `.claude/rules/guided-decisions.md` (Rule 2: every handoff
carries the decision manifest, nuclei never re-ask). Write the rendered output to
`.cex/runtime/handoffs/{{mission}}_{{nucleus}}.md` AND copy to `{{nucleus}}_task.md`
for boot-script consumption (boot scripts are always interactive, task comes from
the file, never a CLI arg).

## Template

```markdown
---
task: dispatch
from: n07
to: {{nucleus}}
mission: {{mission}}
created: "{{iso_date}}"
status: active
related: [{{plan_id}}, {{decision_manifest_ref}}]
---

# Task for {{NUCLEUS_UPPER}} -- {{one_line_task_title}}

## Context (pre-loaded for you)
{{prior_state_summary}}

## DECISIONS (from user -- DO NOT re-ask)
{{decisions_block}}

## Relevant artifacts (READ before producing)
{{numbered_artifact_list}}

## Expected output
{{expected_output_spec}}

## Gates
{{gate_checklist}}

{{acr_prerequisites_block}}
```

## Variables

| Variable | Fills with | Source |
|----------|-----------|--------|
| {{nucleus}} / {{NUCLEUS_UPPER}} | target nucleus id, lower/upper (`n03`/`N03`) | intent resolution (F1) |
| {{mission}} | mission codename, or omitted for a bare solo dispatch | mission plan / user request |
| {{iso_date}} | dispatch timestamp | system clock |
| {{plan_id}} / {{decision_manifest_ref}} | wikilink-style ids of the governing plan + the GDP manifest entry | `.cex/runtime/decisions/decision_manifest.yaml` |
| {{one_line_task_title}} | the precise, transmuted task (never the user's raw phrase verbatim -- see `.claude/rules/n07-input-transmutation.md`) | F1 CONSTRAIN output |
| {{prior_state_summary}} | what is already true/done that the nucleus should NOT redo (dispatch-depth amplifier: cross-reference) | prior signals / git log / prior cell output |
| {{decisions_block}} | either `Read: .cex/runtime/decisions/decision_manifest.yaml :: {{key}}` (GDP already closed) OR, if intent confidence < 0.6, an explicit "defer to GDP" note | GDP protocol |
| {{numbered_artifact_list}} | 2+ concrete paths the nucleus must read before producing (builder ISOs, KC, prior artifact, rule file) -- dispatch-depth amplifier: memory injection | task decomposition |
| {{expected_output_spec}} | exact kind + pillar + path + frontmatter contract + size ceiling for the ONE (or N) artifact(s) expected | `.cex/kinds_meta.json` for the target kind |
| {{gate_checklist}} | compile + doctor threshold + commit scope + signal command, e.g. `compile . doctor {{n}}/{{fail}}/{{warn}} . commit scoped . signal.` | F7/F8 GOVERN+COLLABORATE |
| {{acr_prerequisites_block}} | `## Prerequisites (auto-resolved by ACR)` section, present only for autonomy-enabled kinds (see `.cex/capability_policy.json`); omit entirely otherwise | ACR preflight (`cex_capability_router.py`) |

## Tenant-portability note

The template body above uses `{{repo_root}}`-style path composition implicitly via
relative paths (`.cex/runtime/handoffs/...`) -- it never hardcodes a Central
absolute path. A sovereign tenant repo renders this same form with its own root.

## Provenance (real usage, every session -- the anti-shelf gate for this promotion)

This is N07's single most-used artifact shape and the largest unpromoted corpus
per the R-167 disk audit (N07 had 2 P03 files before this promotion). Cited real
instances:

| Source | What it shows |
|--------|---------------|
| `.cex/runtime/archive/n04_task_20260612_1644.md` | Full 6-section shape: frontmatter (`task: dispatch`, `from`, `to`, `mission`, `related`) + `# Task for N04` + `## Context (pre-loaded for you)` + `## DECISIONS (LOCKED)` + `## Relevant artifacts` (4 numbered paths) + `## Expected output` (exact kind/pillar/size) + `## Gates` + `## Prerequisites (auto-resolved by ACR)` with a low-confidence override note |
| `.cex/runtime/archive/n03_task_20260429_1357.md` | Minimal variant: frontmatter (`nucleus`, `task: dispatch`, `created`) + `# Task for N03` + `## DECISIONS` + `## ON COMPLETION` (commit + signal) -- proves the contract degrades gracefully when depth amplifiers are not needed |
| `.claude/rules/dispatch-depth.md` | The RULE this template renders: "## Context (pre-loaded for you)", "## Relevant artifacts (READ these before producing)", "## Expected output" are mandated section names, not stylistic choices |
| `.claude/rules/guided-decisions.md` Rule 2 | Mandates the `## DECISIONS` section carries the manifest reference on every handoff |
| Every Mode-X `Task tool: dispatch solo\|grid` invocation this session (R-164, R-148, R-156, R-166/R-167 itself) | This template's rendered form is what gets written before each of those dispatches |

Every session writes 1-6+ of these; the shape has been stable since at least
2026-04 (n03_task_20260429) through 2026-06 (n04_task_20260612) with only additive
sections (ACR Prerequisites added later, never replacing the core 4).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_pt_n07_workflow_build_cell]] | sibling (P03 N07 set) | 0.35 |
| dispatch-depth | upstream | 0.60 |
| guided-decisions | upstream | 0.50 |
| n07-orchestrator | upstream | 0.55 |
