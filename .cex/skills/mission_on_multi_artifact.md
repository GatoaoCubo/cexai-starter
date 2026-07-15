---
name: mission-on-multi-artifact
description: Promote a /build into /mission via cex_mission_runner when the plan requires three or more artifacts so wave orchestration handles dependencies.
when:
  - The resolved plan from /plan or /spec lists three or more artifacts.
  - Multiple nuclei must run with cross-wave handoffs to deliver one outcome.
  - User says "do all of it" or implies a full lifecycle with dependencies.
kind: skill
pillar: P04
nucleus: all
quality: null
version: 1.0.0
created: 2026-04-27
updated: 2026-04-27
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.85
tags: [skill, autofire, mission, orchestration, autowire, layer6]
related:
  - n07-orchestrator
  - guided-decisions
  - composable-crew
  - p01_kc_orchestration_best_practices
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_mission_runner. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Mission on Multi Artifact

## When this fires
- /plan output lists 3+ artifacts.
- /spec produces a wave plan with multiple nuclei.
- The user requests a full lifecycle (research -> spec -> build -> ship -> measure).

## What to do
1. Do NOT call `Task tool: dispatch solo` for this work; promote it to a mission instead.
2. Verify a decision_manifest.yaml exists; if not, run /guide first to lock subjective choices BEFORE dispatch.
3. Run `python _tools/cex_mission_runner.py --spec <path> --waves auto --execute` to orchestrate the full plan.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
4. The mission runner reads the spec, computes waves, dispatches grids, polls signals, gates between waves, and consolidates at the end.
5. Honor the spec's `wave_order` and `depends_on` fields; do not flatten waves into one grid unless the dependency graph allows.
6. After completion, mission runner archives signals to `.cex/runtime/archive/<mission>_<ts>/` -- never delete signals manually.

## Example
- User says `launch a Black Friday campaign end-to-end`. /plan produces 12 artifacts across 3 waves. Skill fires `cex_mission_runner --spec spec_bf_launch.md --waves auto --execute`. Mission runs research wave, then creative wave, then ops wave, with quality gates between each. User checks back to a fully-shipped campaign.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| n07-orchestrator | upstream | 0.80 |
| guided-decisions | upstream | 0.70 |
| composable-crew | sibling | 0.60 |
| p01_kc_orchestration_best_practices | upstream | 0.55 |
