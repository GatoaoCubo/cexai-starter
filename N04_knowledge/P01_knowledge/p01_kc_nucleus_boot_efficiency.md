---
id: p01_kc_nucleus_boot_efficiency
kind: knowledge_card
kc_type: meta_kc
pillar: P01
nucleus: n04
version: 1.0.0
created: "2026-06-13"
updated: "2026-06-13"
title: "CEXAI Nucleus Boot Efficiency -- Thin Boot + claudeMdExcludes (Phase A + A.5)"
domain: orchestration-infrastructure
subdomain: boot-efficiency
quality: null
review_date: "2026-09-13"
tags:
  - boot-efficiency
  - thin-boot
  - token-economics
  - prompt-cache
  - cex-thin-boot
  - nucleus-spawn
primary_8f: INJECT
slots:
  query_context: "how to reduce nucleus boot token cost per spawn"
  target_audience: "n07 orchestrator, n03 builder, cex operators"
tldr: "Every builder spawn pays ~30k boot tokens; Phase A+A.5 cuts 10.2k/spawn (~32-35%) via a stable shared prefix + claudeMdExcludes that de-auto-loads N07-only rules for n01-n06. OFF = byte-identical fallback. Constitution never excludable."
related:
  - rule_n07_admin
  - nucleus_def_n07
  - nucleus_def_n01
  - nucleus_def_n06
  - bld_knowledge_card_nucleus_def
  - p01_rm_cex
  - bld_collaboration_nucleus_def
  - nucleus_def_n05
  - p02_mm_cex_architecture_n04
  - nucleus_def_n03
---

## Quick Reference

```yaml
topic: CEXAI nucleus boot efficiency (Phase A + A.5, shipped 2026-06-13)
scope: builders n01-n06; n07 excluded (orchestrator, owns those rules)
owner: n03 (commits 838da545c2 + 8f2c2a30f5)
criticality: high -- boot tax is the #1 rate-limit drain on the Max plan
```

## Overview

- Every nucleus spawn: CLAUDE.md + all rules/*.md auto-loaded = ~30k token base
- 6-cell grid: ~180k boot tokens consumed before any artifact byte is produced
- On Max: boot loops exhaust the rate-limit window faster than actual builds do
- Phase A+A.5 (2026-06-13): 10,227 tok/builder/spawn saved (~32-35% reduction)

## Boot Tax Root Cause

Claude Code AUTO-LOADS every rules/*.md at each spawn. Token breakdown:

| Layer | Tokens | Characteristic |
|-------|--------|----------------|
| CLAUDE.md + 12 rules files | ~16.8k | Stable; identical across all nuclei |
| Per-nucleus ISOs + KCs | ~8-10k | Varies by nucleus and top-k selection |
| Agent card + constitution | ~3k | Constant per spawn |
| **Total baseline** | **~30k** | Paid before any artifact work begins |

N07-only rules (n07-orchestrator + n07-input-transmutation) account for ~10.2k of
the shared rules load. Builders n01-n06 never need orchestrator routing rules --
this is the extractable slice: present in every builder boot, unused by builders.

## Phase A -- Assembler (commit 838da545c2)

Splits the boot into a stable shared prefix (prompt-cacheable) + a thin per-nucleus slice:

```
boot(nucleus) = [ STABLE SHARED PREFIX ]  <- prompt-cached; identical across nuclei
             +  [ THIN NUCLEUS SLICE ]     <- per-nucleus; 3.8k-6.0k tokens
                  - n0X own rules only
                  - owned-kind ISOs (top-k, ranked by cex_preflight ranker)
                  - relevant KCs (top-k)
```

Artifacts created in Phase A:
- cex_boot_context.py: assemble() per nucleus; --emit/--measure/--verify flags
- capability_registry_nucleus_kinds: nucleus->kinds map; 304 kinds, 0 orphans
- p02_boot_cex_thin_assembly: assembly policy (prefix set, top-k, TTL/warm strategy)
- test_cex_boot_context.py: 64 tests; OFF byte-identical proven n01-n06

Measured thin slices (target: slice <=9k, warm reduction >=60%):

| Nucleus | Thin slice | Warm input reduction | Gate |
|---------|-----------|---------------------|------|
| n01 | ~3.8k | ~87.3% | PASS |
| n02 | ~4.1k | ~85.6% | PASS |
| n03 | ~5.9k | ~81.2% | PASS |
| n04 | ~4.5k | ~84.7% | PASS |
| n05 | ~6.0k | ~80.9% | PASS |
| n06 | ~4.2k | ~85.1% | PASS |

## Phase A.5 -- Realized Cut (commit 8f2c2a30f5)

Phase A had a trap: it APPENDED the assembled prefix, but Claude Code still auto-loaded
the full rules set on top. CEX_THIN_BOOT=1 ADDED context, not cut it.

A.5 uses the native claudeMdExcludes overlay mechanism to realize the cut.
When CEX_THIN_BOOT=on, resolve_model.ps1 emits ONE combined settings file:

- Nucleus stub: permissions + L2 UserPromptSubmit hook (constitution enforcement)
- MERGED with: claudeMdExcludes targeting the two N07-only rules files

Why ONE file: --settings is last-wins-on-disk; a separate thin overlay would drop
the L2 constitution hook. Single merged file = hook always present = always safe.

Excluded for n01-n06: n07-orchestrator + n07-input-transmutation (~10.2k total)
Preserved: 8f-reasoning, ascii-code-rule, ubiquitous-language, guided-decisions,
           composable-crew, raci-matrix, dispatch-depth, system-overview (all 8)

Realized numbers (disk-measured on n01 via claude -p sentinel, cache-independent):
- 10,227 tokens saved per builder spawn
- ~32-35% of the ~30k boot baseline
- ~61k saved per 6-builder wave (before any prompt cache warm kicks in)
- Canary: N07 rules ABSENT, 8F + constitution INTACT -- VERIFIED on disk

See p07_bm_boot_tax for full per-nucleus benchmark data.

## Safety Spine

Three non-negotiables that CEX_THIN_BOOT cannot violate:

1. **OFF = byte-identical**: any thin settings failure -> degrade to full context stub
   (plain nucleus stub; runtime args byte-identical to today's boot)
2. **Constitution never excludable**: not a rule; outside claudeMdExcludes scope;
   --verify guard asserts it is present on every thin boot emit
3. **n07 never excluded**: orchestrator owns those rules; scope = n01-n06 only

Reference (Anthropic prompt caching, 5-min TTL the stable prefix exploits):
https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

## Axioms

- Default CEX_THIN_BOOT=1 for all steady-state n01-n06 builder dispatches
- Run cex_boot_context.py --verify before any thin boot deployment change
- Never exclude constitution, 8f-reasoning, or L2 hooks; only N07-only rules
- Measure with cex_token_budget.py: disk numbers only (not projections)
- The ~10.2k saving is cache-independent -- it applies on cold boots too

## Decision Rules

| Condition | Setting | Notes |
|-----------|---------|-------|
| Steady-state builder dispatch n01-n06 | CEX_THIN_BOOT=1 | ~10.2k savings/spawn |
| n07 orchestrator boot | N/A | n07 always full; flag not applicable |
| Debugging missing context in builder | CEX_THIN_BOOT=0 | Byte-identical full context |
| Rate-limit window tight | 1 + decompose | Compounds: thin boot + F6-only model |
| Worktree dispatch (-w flag) | 1 (safe) | Per-worktree settings; no conflict |
| New nucleus N08+ | assess | Must add to excludable_rule_paths first |

## Acceptance Criteria (Phase A -- all gates passed 2026-06-13)

| Gate | Target | Actual |
|------|--------|--------|
| Thin slice size n01-n06 | <=9k tokens | 3.8k-6.0k PASS |
| Warm input reduction | >=60% | 80.9-87.3% PASS |
| OFF = byte-identical | 100% | 3753 tests passed PASS |
| doctor check | 302/0/0 | 302/0/0 PASS |
| ASCII clean (.py/.ps1) | 0 violations | 0 violations PASS |
| Constitution + L2 hook intact | always | --verify guard active PASS |


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[rule_n07_admin]] | downstream | 0.39 |
| [[nucleus_def_n07]] | downstream | 0.36 |
| [[nucleus_def_n01]] | downstream | 0.35 |
| [[nucleus_def_n06]] | downstream | 0.33 |
| [[bld_knowledge_nucleus_def]] | sibling | 0.33 |
| p01_rm_cex | related | 0.32 |
| [[bld_orchestration_nucleus_def]] | downstream | 0.32 |
| [[nucleus_def_n05]] | downstream | 0.31 |
| [[p02_mm_cex_architecture_n04]] | related | 0.31 |
| [[nucleus_def_n03]] | downstream | 0.31 |
