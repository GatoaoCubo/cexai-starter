---
quality: null
id: n00_genesis_rules
kind: instruction
pillar: P08
glob: "N00_genesis/**"
description: "N00 Genesis Nucleus -- the pre-sin archetype; reference-only, never dispatched"
title: "N00-Genesis"
version: "1.0.0"
author: n00_lane_grid_g1
tags: [nucleus-rules, n00, genesis, archetype, reference-only]
tldr: "N00 identity + editing rules: no sin lens, no boot script, never dispatched. It is the 12-pillar schema/kind-manifest substrate every N01-N07 (and every tenant) reads at F1 CONSTRAIN / F3 INJECT. Closes register row R-100 -- every other nucleus has a rules/n0X-*.md; N00's rules/ held only a .gitkeep before this file."
domain: "CEX system"
created: "2026-07-05"
updated: "2026-07-05"
8f: "F2_become"
keywords: [pre-sin archetype, pillar schemas, kind manifests, reference-only, never dispatched, convention-over-configuration]
density_score: 0.85
related:
  - nucleus_def_n00
  - agent_card_n00
---

# N00 Genesis Rules

## Identity

1. **Role**: Pre-sin archetype -- the structural template every nucleus (N01-N07) is cloned from.
2. **CLI**: none. N00 has no boot script, no model tier, no CLI binding (`cli_binding: reference-only` in `nucleus_def_n00.md`).
3. **Domain**: archetype -- 12 pillar `_schema.yaml` files + 268 kind manifests (see `component_map_n00.md` for the live count).

## When You Are Asked to "Be" N00

You are not. N00 cannot be booted, spawned, or dispatched -- confirmed
structurally excluded from every launcher on disk:

- `Task tool: dispatch solo n00 "task"` -- rejected (`n0[1-7]` regex, 3 sites in `Task tool: dispatch`)
- `boot/cex_nucleus.sh n00` -- file exists but its own guard rejects `n00` (`^n0[1-7]$`)
- `boot/n00.ps1` -- absent; no boot script family exists for N00

If a task genuinely requires N00's persona (e.g. "explain the archetype, F2
BECOME the genesis identity for reasoning purposes"), that is a **read-only F3
INJECT** of `nucleus_def_n00.md` + this file by whichever nucleus is actually
executing -- never an actual dispatch to `n00`.

## Editing N00's Content

N00 has no self-execution path. It is populated and maintained EXCLUSIVELY by
other nuclei editing it directly:

1. **Standing rule**: `.cex/P09_config/dispatch_catalog.md` lists
   `N00_genesis/P*/*.md` as a **FORBIDDEN path -> N03**. N07's default posture
   is to dispatch N03 to touch N00 content, never edit it directly itself.
2. **Historical precedent**: `FLYWHEEL_N00_n0X` handoffs instructed OTHER
   nuclei (N01-N05) to deep-enrich N00 artifacts inside their OWN git
   worktrees -- N00 has never been, and structurally cannot be, the actor.
3. **Grid-scoped exception**: an explicit multi-lane grid dispatch may assign
   a `N00_genesis/` lane directly to a bounded subagent cell (as opposed to
   routing through N03) when the orchestrating parent partitions the tree
   itself -- this rule file's own creation is an example. The FORBIDDEN-path
   rule governs N07's own default unscoped behavior, not a lane an
   orchestrator has explicitly carved out and granted.

## Content Rules (for whoever is editing)

1. Every kind manifest, schema, and KC in N00 is the schema-of-record every
   nucleus and tenant reads -- treat edits here as touching shared
   infrastructure, not a single nucleus's private territory.
2. `quality: null` on every artifact (peer review only, never self-scored) --
   same universal rule as everywhere else in CEX.
3. Compile after save: `python _tools/cex_compile.py {path}`.
4. Never invent a pillar that doesn't exist (P01-P12 only -- see register row
   R-101, a real bug where `nucleus_def_n00.md` cited a nonexistent `P00` until
   2026-07-05).
5. Counts drift fast here (268 kind manifests, 317 registered kinds, 1,411
   `.md` files -- all as of 2026-07-05). Cite a verification date whenever you
   write one down; do not assume a prior count is still current (see register
   rows R-072/R-130, a repeating disease across this repo's nucleus cards).

## Sin Lens: None (Pre-Sin)

N00 is the one nucleus with no sin lens. It optimizes for nothing -- it is
inert reference data, not an agent with a cultural-DNA tiebreaker. Do not
assign it Envy/Lust/Pride/Gluttony/Wrath/Greed/Sloth; that would collapse the
archetype/instance distinction the whole nucleus system depends on.

## Routing

| Route TO N00 | Route AWAY from N00 |
|---------------|----------------------|
| Nothing -- N00 is never a dispatch target | Any user-facing task (route to N01-N07 per `.claude/rules/n07-orchestrator.md`) |
| (read-only) F1 CONSTRAIN / F3 INJECT by any nucleus | Any request to "boot" or "run" N00 -- structurally impossible |
| Editing N00's own content, via N03 or an explicit grid-scoped lane grant | Scaffolding a NEW nucleus (N08+) -- that's `_tools/cex_new_nucleus.py`, which treats N00-N07 as reserved and does not touch N00 at scaffold time |

## Properties

| Property | Value |
|----------|-------|
| Kind | instruction |
| Pillar | P08 |
| Domain | archetype |
| Pipeline | none (N00 never runs 8F itself; the EDITING nucleus does) |
| CLI binding | reference-only |
| Model tier | none |
| Quality target | 8.0 min / 9.0+ target (for content produced ABOUT N00) |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[nucleus_def_n00]] | upstream (machine-readable identity) | 0.60 |
| [[agent_card_n00]] | sibling (capability declaration) | 0.50 |
| component_map_n00 | sibling (inventory) | 0.45 |
| n00_readme | sibling (human-facing guide) | 0.40 |
| n07-orchestrator | related (the only path that may route work to N00's content) | 0.35 |
