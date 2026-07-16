---
id: nucleus_def_n01
kind: nucleus_def
pillar: P02
nucleus: N01
nucleus_id: N01
role: intelligence
title: "N01 Intelligence -- Nucleus Definition"
version: "1.1.0"
created: "2026-04-27"
updated: "2026-07-05"
quality: null
density_score: 0.92
domain: "research/analysis"
sin_lens: "Analytical Envy"
cli_binding: claude
model_tier: sonnet
model_specific: claude-sonnet-4-6
context_tokens: 200000
boot_script: boot/n01.ps1
agent_card_path: N01_intelligence/agent_card_n01.md
pillars_owned:
  - P01
crew_templates_exposed:
  - taxonomy_audit
  - competitor_scan
domain_agents:
  - agent_market_analyst   # aspirational -- no file exists under this name (R-145 audit, 2026-07-07)
  - agent_paper_reader     # aspirational -- built as agent_paper_reviewer.md instead, not wired as a Task-tool subagent (R-145 audit, 2026-07-07)
fallback_cli: codex
related:
  - agent_card_n01
  - kc_nucleus_def
tags: [nucleus_def, n01, identity]
---

# N01 Intelligence -- Nucleus Definition

Machine-readable identity contract for N01 INTELLIGENCE. Loaded by `cex_router.py`,
`cex_dispatch`, and per-nucleus boot scripts. Maps a nucleus's role to its
operational scope, sin lens, and quality contract.

> **Consolidation note (2026-07-05):** this file merges the two historical
> `nucleus_def_n01.md` copies (register row R-026). Canonical path is
> `P02_model/` per `.claude/rules/new-nucleus-bootstrap.md` (9-asset table) and
> `_tools/cex_new_nucleus.py::render_nucleus_def()`. The former
> `P08_architecture/nucleus_def_n01.md` copy is removed (content lives on here
> + in git history); its `cli_binding` / `model_tier` / `model_specific` /
> `context_tokens` / `pillars_owned` / `crew_templates_exposed` /
> `domain_agents` fields and its Pillars Owned / Crew Templates Exposed /
> Domain Agents / Boot Contract / Composability sections are folded in below.
> A 2026-07-03 N01 self-review (`P07_evals/self_review_fractal_2026_07_03.md`,
> finding D-02) had marked THIS file `status: deprecated` in favor of the
> P08_architecture copy, reasoning that the P08 copy alone had the
> `model_specific`/`context_tokens` fields. That review's fix direction is
> reversed here in favor of completing the merge toward the documented
> canonical path instead: the content gap it correctly identified is closed by
> the merge (this file now carries every P08-only field), so a path-level
> deprecation is no longer needed. The `status`/`superseded_by`/deprecated
> `when_to_use` fields are removed accordingly.

## Identity

| Field | Value |
|-------|-------|
| **Nucleus ID** | `n01` |
| **Full name** | N01 Intelligence |
| **Domain** | research/analysis |
| **Sin lens** | Analytical Envy |
| **Pillar (definition)** | P02 (Model) |
| **CLI binding** | claude |
| **Model tier** | sonnet (`claude-sonnet-4-6`) |
| **Context** | 200K tokens |
| **Fallback CLI** | codex |

## Sin Lens

**Analytical Envy** -- this nucleus optimizes for the sin's first word when the task is ambiguous. Two ambiguous goals tie -- sin breaks tie.

## Operational Scope

This nucleus owns work in the **research/analysis** domain. Tasks routed here when:

- Research, competitive analysis, market intel
- Benchmarking peers / reading papers
- Comparative reasoning required

## Pillars Owned

| Pillar | Domain | Sample Kinds |
|--------|--------|--------------|
| P01 | knowledge | knowledge_card, rag_source, research_pipeline |

## Crew Templates Exposed

| Template | Role in Crew | Inputs | Outputs |
|----------|--------------|--------|---------|
| taxonomy_audit | researcher | repo scan | audit report |
| competitor_scan | market_researcher | product spec | competitive matrix |

## Domain Agents

> **Status (R-145 verify, 2026-07-07): both rows below are aspirational, not shipped.**
> Neither `agent_market_analyst` nor `agent_paper_reader` exists as a file under that name
> anywhere in the repo, and neither is wired as an invocable Task-tool subagent (no
> `.claude/agents/*.md` definition for either name -- that directory holds 321 files total: 318
> kind-builder subagents, one general `validator.md`, and exactly two nucleus-level personas
> belonging to OTHER nuclei (`n02-marketing.md`, `n04-knowledge.md`); N01 has no nucleus-level
> persona there either). N01's `Agent(*)`
> permission (`.claude/nucleus-settings/n01.json`) lets N01 invoke the Agent/Task tool
> mechanically, but there is no target for it to reach either declared name today. The closest
> real artifacts are `agent_paper_reviewer.md` (id `p02_agent_paper_reviewer` -- an `agent`-kind
> design/spec document, built under a different name than declared here) and
> `agent_competitor_tracker.md` (built, and not listed in this table at all) -- both live at the
> Path below, both are content/spec documents, and neither is a Task-tool subagent definition.
> Building real, wired agent personas for N01 is authorial N01 work, out of scope for this
> verify pass; recommended as a follow-up.

| Agent | Purpose | Path |
|-------|---------|------|
| agent_market_analyst | Competitive analysis | NOT BUILT -- no file under this name anywhere in the repo |
| agent_paper_reader | Academic paper synthesis | NOT BUILT under this name -- see `N01_intelligence/P02_model/agent_paper_reviewer.md` |

## Quality Contract

| Aspect | Value |
|--------|-------|
| Min score to publish | 8.0 |
| Target score | 9.0+ |
| Self-scoring | NEVER (peer review only) |
| 8F mandatory | YES |

## Boot Contract

- Boot file: `boot/n01.ps1`
- Task source: `.cex/runtime/handoffs/n01_task.md`
- Signal: `write_signal('n01', 'complete', {score})`
- Signal path: `.cex/runtime/signals/signal_n01_*.json`

## Composability

| Direction | Nucleus | What Flows |
|-----------|---------|-----------|
| outbound | N02, N04 | positioning briefs, market intel |
| outbound | N06 | competitor pricing data |
| inbound | N07 | research handoffs |
| inbound | N04 | taxonomy gaps to research |

## Related Files

- **Agent card**: [N01_intelligence/agent_card_n01.md](../agent_card_n01.md)
- **Boot script (Windows)**: `boot/n01.ps1`
- **Boot script (cross-platform)**: `boot/cex_nucleus.sh n01`
- **Per-nucleus rule**: `.claude/rules/n01-*.md` (N07: `n07-orchestrator.md`)

## Routing Hints

This nucleus answers when the user intent maps to:
- **Verbs**: research, analyze, benchmark, compare

See `.claude/rules/n07-input-transmutation.md` for the full verb-to-nucleus mapping.

### How to use

```text
ROLE: You are an orchestrator resolving whether to route work to N01.
ACT:
  - Match the task domain against N01 declared capabilities here.
  - Respect the routing + RACI: N01 researches/analyzes; it does not score itself.
  - Use the sin lens (Analytical Envy) as N01 optimization bias.
OUTPUT: a route/no-route decision for N01 with the matched capability.
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| agent_card_n01 | sibling | 0.95 |
| n07-orchestrator | upstream | 0.85 |
| [[nucleus_def_n00]] | upstream | 0.80 |
| [[kc_nucleus_def]] | upstream | 0.48 |
| component_map_n01 | downstream | 0.42 |
