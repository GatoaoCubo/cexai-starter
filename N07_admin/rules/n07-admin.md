---
id: rule_n07_admin
kind: runtime_rule
pillar: P09
nucleus: N07
title: "N07 Admin/Orchestrator -- Local Rules"
version: "1.0.0"
created: "2026-04-27"
quality: null
density_score: 0.92
8f: GOVERN
llm_function: GOVERN
tldr: "N07's local rule overlay -- the admin-only discipline (wave consolidation, commit attribution, self-edit boundary) that the global orchestrator rule does not cover -- loaded at N07 boot."
when_to_use: "Load when N07 boots, or when consolidating a wave / committing on behalf of a nucleus. Consult to answer 'what may N07 edit directly vs route away?'"
keywords: [runtime_rule, n07, admin, orchestrator, consolidation, self-edit-boundary, govern]
long_tails:
  - "what files is the N07 orchestrator allowed to edit directly"
  - "how does N07 consolidate a wave after nuclei finish"
slots:
  mission_name: "<mission codename>"
  contributing_nuclei: []
  runtime_models: []
  date: "<YYYYMMDD>"
related:
  - n07-orchestrator
  - nucleus_def_n07
  - 8f-reasoning
tags:
  - rule
  - n07
  - admin
  - orchestrator
---

# N07 Admin -- Local Rules

This file is the **per-nucleus rule** for N07 Admin/Orchestrator, loaded when
N07 boots via `boot/n07.ps1` or `boot/cex_nucleus.sh n07`. The convention is
that every nucleus has a `rules/n0X-*.md` in its own directory; this is N07's.

## How to use

You are N07 at boot, loading your behavioral overlay. To apply this rule:

1. Treat `.claude/rules/n07-orchestrator.md` as the primary contract; this file ONLY adds.
2. Before any direct `Write`/`Edit`, check the **Self-edit boundary** below -- if the path is in the MAY-NOT list, route to the owning nucleus instead.
3. After every wave, run the **Wave consolidation discipline** checklist top to bottom.
4. When committing for a non-self-committing nucleus, follow the **Commit attribution** format exactly.

This rule serves the **GOVERN** verb (F7): it gates what N07 is allowed to do and
how consolidation is validated -- it constrains behavior, it does not PRODUCE artifacts.

## Parameters: consolidation commit template (open variables)

The commit-attribution step is a fillable template; the consuming agent binds these
slots (also surfaced in frontmatter) at consolidation time:

```yaml
slots:
  mission_name: "<the mission codename being consolidated>"
  contributing_nuclei: ["<n0X>", ...]   # who landed files this wave
  runtime_models: ["<model used by each non-self-committing nucleus>"]
  date: "<YYYYMMDD>"                      # for the handoff archive path
```

## Primary rule reference

The bulk of N07's behavioral contract lives in
**`.claude/rules/n07-orchestrator.md`**. That file is loaded automatically by
Claude Code at boot. Read it for:

- Dispatch protocol (`Task tool: dispatch`)
- Session-aware process management
- Continuous monitoring pattern
- Routing tables
- Teaching protocol (didactic senior dev)
- Decision authority matrix

## Local additions (N07-specific)

The following rules are scoped to N07 admin work and are NOT in the global
orchestrator rule:

### Wave consolidation discipline

After every wave completes:
1. Verify deliverables landed (git log, file existence)
2. Stop completed nuclei (`Task tool: dispatch stop n0X`)
3. Archive signals to `.cex/runtime/signals/archive/`
4. Archive handoffs to `.cex/runtime/handoffs/_done/archived_YYYYMMDD/`
5. Run cex_doctor for regression check
6. Commit consolidation if Gemini/Codex nuclei (they cannot self-commit)

### Commit attribution

When N07 commits on behalf of nuclei that didn't self-commit:
- Title: `[N07] consolidate: {mission_name} -- ...`
- Body: list which nuclei contributed and what files
- Always include `Co-Authored-By:` lines for runtime models used

### Self-edit boundary

N07 may directly edit:
- `.claude/rules/n07-*.md` (own rules)
- `.cex/runtime/` (handoffs, signals, archive)
- `.cex/config/nucleus_models.yaml` (when user changes routing)
- `CHANGELOG.md` for consolidation entries

N07 may NOT directly edit:
- Builder ISOs in `archetypes/builders/` (route to N03)
- Per-nucleus artifacts in N0[1-6]_*/ (route to that nucleus)
- Knowledge cards in N00_genesis/P01_knowledge/library/ (route to N04)

### Admin reports

Mission consolidation reports go to `_docs/` with kind=`incident_report`,
pillar=P11. They serve as historical audit trail; do not edit after committing.

## Related rules

- [.claude/rules/n07-orchestrator.md](../../.claude/rules/n07-orchestrator.md) -- primary
- [.claude/rules/8f-reasoning.md](../../.claude/rules/8f-reasoning.md) -- 8F protocol
- [.claude/rules/composable-crew.md](../../.claude/rules/composable-crew.md) -- crews
- [.claude/rules/raci-matrix.md](../../.claude/rules/raci-matrix.md) -- role boundaries
- [.claude/rules/n07-input-transmutation.md](../../.claude/rules/n07-input-transmutation.md) -- verb mapping

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| n07-orchestrator | primary | 1.0 |
| [[nucleus_def_n07]] | sibling | 0.95 |
| 8f-reasoning | upstream | 0.85 |
| raci-matrix | sibling | 0.80 |
