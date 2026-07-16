---
id: agent_card_n00
kind: agent_card
8f: F2_become
pillar: P08
nucleus: n00
title: "N00 Genesis -- Agent Card (Reference-Only, Never Dispatched)"
version: "1.0.0"
created: "2026-07-05"
author: n00_lane_grid_g1
domain: archetype
quality: null
tags: [agent_card, n00, genesis, archetype, reference-only]
density_score: 0.85
tldr: "N00 has no deployable identity. This card documents that absence structurally (model: none, tools: none, dispatch: never) so nucleus_def_n00.md's agent_card_path has a real, resolvable target instead of a dangling reference (register row R-098)."
keywords: [n00, genesis, archetype, reference-only, never-dispatched, pre-sin]
related:
  - nucleus_def_n00
---

# N00 Genesis -- Agent Card

> **This card exists to close a dangling reference** (register row R-098):
> `nucleus_def_n00.md`'s `agent_card_path` field cited this file before it
> existed anywhere on disk (confirmed absent via `find` prior to this fix;
> independently flagged in `docs/NUCLEUS_ARCHITECTURE_DOSSIER.md`'s N00 card,
> "Dead references found"). Unlike every other agent_card in the system, this
> one documents an ABSENCE of deployability, not a live capability -- N00 is
> the pre-sin archetype, never instantiated for production work.

## Routing

- **Priority**: n/a -- N00 is structurally never a dispatch target.
- **Keywords**: none. N00 is not addressable by user intent; `.claude/rules/n07-input-transmutation.md`'s mapping table has no N00 row (N01-N07 only).
- **Dispatch**: NEVER. Confirmed excluded from all 3 launch mechanisms on disk:

| Mechanism | Status | Evidence |
|-----------|--------|----------|
| `Task tool: dispatch solo n00 "task"` | REJECTED | nucleus tokens parsed via `n0[1-7]` regex (3 sites in `Task tool: dispatch`) |
| `boot/cex_nucleus.sh n00` | REJECTED | file exists but its own guard (`L20`) is `[[ ! "$NUCLEUS" =~ ^n0[1-7]$ ]]` |
| `boot/n00.ps1` (or any CLI variant) | ABSENT | no boot script family for N00 exists |

## Provider

| Mode | Provider | When |
|------|----------|------|
| n/a | none | `model_tier: none` in `nucleus_def_n00.md` -- N00 has no runtime model binding |

## Capabilities Map

N00 produces nothing at runtime -- it IS the produced-from substrate. It holds
12 pillar `_schema.yaml` files (the only 12 that exist anywhere in the repo)
plus 268 `kind_manifest_n00.md` files (one per modeled kind, see
`component_map_n00.md` for the live per-pillar breakdown) that every other
nucleus's F1 CONSTRAIN reads on every single build, in Central and in every
distilled tenant.

| Capability | Input | Output Template |
|-----------|-------|-----------------|
| _None -- reference-only, never executes_ | n/a | n/a |

## Anti-Patterns (Route AWAY)

| Don't Use For | Route To Instead | Why |
|---------------|------------------|-----|
| "Update N00's kind schemas / manifests" | N03 (`.cex/P09_config/dispatch_catalog.md` L100: `N00_genesis/P*/*.md` is a FORBIDDEN path -> N03) | N00 has no self-execution path; N07 must dispatch another nucleus (normally N03, or a specific grid-scoped lane grant) to edit N00 content -- N00 never edits itself |
| "Boot N00" / "dispatch n00" | n/a -- structurally impossible today | No boot script, no CLI binding, excluded by regex from every launcher (see Routing table above) |
| "Give N00 a sin lens" | n/a | N00 is deliberately pre-sin -- the archetype every sin-bearing nucleus (N01-N07) is cloned from; instantiating a sin on N00 itself would break the archetype/instance distinction |

## Inter-Nucleus Handoffs

| From | To N00 | What |
|------|--------|------|
| N07 (routed through N03 or an explicit grid-scoped lane grant) | content edits | Historical precedent: `FLYWHEEL_N00_n0X` handoffs instructing another nucleus to deep-enrich N00 artifacts inside ITS OWN worktree |

| From N00 | To | What |
|----------|-----|------|
| (passive read, every build) | N01-N07, every tenant | `P{01-12}_*/_schema.yaml` (F1 CONSTRAIN), `P01_knowledge/library/kind/kc_{kind}.md` (F3 INJECT) |

## Composable Crews

_None._ N00 owns zero `crew_template` instances and never participates in a crew.

## Quality Contract

| Aspect | Value |
|--------|-------|
| Min score to publish | 8.0 (applies to content produced ABOUT N00 by the dispatching nucleus) |
| Target score | 9.0+ |
| Self-scoring | N/A -- N00 never executes, so it never self-scores |
| 8F mandatory | Only for whichever nucleus is dispatched to edit N00 content |

## Boot Contract

_Not applicable_ -- N00 is never spawned. See `nucleus_def_n00.md`'s Boot Contract section (identical conclusion, machine-readable form).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[nucleus_def_n00]] | sibling (identity contract) | 0.85 |
| component_map_n00 | sibling (inventory) | 0.55 |
| n00_readme | upstream | 0.40 |
| n07-orchestrator | related (only path that may route work to N00's content) | 0.35 |
