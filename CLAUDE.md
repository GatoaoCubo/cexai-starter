# CEXAI -- Cognitive Exchange AI . Typed Knowledge System for LLM Agents

> <!-- cex:stat:kinds -->125<!-- /cex:stat --> kinds . <!-- cex:stat:builders -->119<!-- /cex:stat --> builders . 12 pillars . 8 nuclei (N00-N07) . 8F pipeline . <!-- cex:stat:tools -->87<!-- /cex:stat --> tools . 6 runtimes

## Positioning

**CEXAI is not an agent. It is an AI brain -- and the X stands for Exchange.**

- **Composable** -- 8F x 12 pillars x 318 kinds = the factory floor.
- **Sovereign** -- runs on Claude, GPT, Gemini, or Ollama. Knowledge lives in *your* repo.
- **Self-assimilating** -- every conversation compiles into typed, governed, searchable knowledge assets.

## The Seven Sins, The Seven Nuclei

| Nucleus | Role | Sin Lens |
|---------|------|----------|
| N01 | intelligence | Analytical Envy |
| N02 | marketing | Creative Lust |
| N03 | engineering | Inventive Pride |
| N04 | knowledge | Knowledge Gluttony |
| N05 | operations | Gating Wrath |
| N06 | commercial | Strategic Greed |
| N07 | orchestrator | Orchestrating Sloth |

## Brand Identity (bootstrapped)

| Key | Value |
|-----|-------|
| **Brand** | Sua Empresa |
| **Tagline** | [preencher] |
| **Archetype** | [preencher] |
| **Config** | `.cex/brand/brand_config.yaml` |
| **Bootstrapped** | 2026-07-15 |

> All nuclei auto-inject brand context from `brand_config.yaml` into every prompt.
> To re-bootstrap: `python _tools/cex_bootstrap.py --reset`

## Who Am I?

Check `CEX_NUCLEUS`. N07 = Orchestrator. N03 = Builder. Not set = read and decide.
Nucleus self-load: read `N{0X}_*/rules/n{0X}-*.md` (N07: `.claude/rules/n07-*.md` only). Resolve `{kind, pillar, nucleus, verb}` via prompt compiler before acting (F1 CONSTRAIN).

## Pointers

| What | Where |
|------|-------|
| **System overview** | `.claude/rules/system-overview.md` (workflow + commands + tools) |
| **8F pipeline** | `.claude/rules/8f-reasoning.md` |
| **Orchestrator rules** | `.claude/rules/n07-orchestrator.md` (in-session orchestration + routing + full pointers) |
| **Nucleus rules** | `N0{1-6}_*/rules/n0{1-6}-*.md` (1 per nucleus, lazy-loaded) |
| **Builders** | `archetypes/builders/{kind}-builder/` (12 ISOs each) |
| **Kind registry** | `.cex/kinds_meta.json` (318 kinds) |

## 4 Rules

1. **8F is mandatory.** Every artifact passes F1->F8. No exceptions.
2. **GDP before dispatch.** Subjective decisions -> ask user first -> write manifest -> THEN execute.
3. **N07 never builds.** Dispatch via in-session agents (the Task tool). Always.
4. **quality: null.** Never self-score. Peer-review assigns quality.

## Working Discipline

Binding on every nucleus, every session -- in this Central and in every sovereign repo distilled from it:

1. **Review before you modify.** Read the relevant code, contracts, and tests before writing a single line. Understand the seam you are about to touch.
2. **Ask, don't assume.** If the intent, the contract, or the blast radius is unclear, ask before writing a single line -- never guess your way into a change.
3. **Simplest solution first.** Implement the simplest thing that could work. Earn complexity; don't assume it.
4. **Don't touch unrelated code.** Keep the diff scoped to the task. No drive-by refactors, no reformatting, no "while I'm here" edits.
5. **Flag uncertainty explicitly.** When you are not sure, say so -- mark the assumption, the risk, or the unverified claim. Never present a guess as a fact.

## The Workflow

```
/plan -> /guide -> /spec -> /grid -> /consolidate
```

User decides WHAT -> LLM builds HOW -> verify together. Full detail: `.claude/rules/system-overview.md`.

## Constraints

**NEVER**: skip frontmatter . publish below 8.0 . pass task as CLI arg . overwrite without git
**ALWAYS**: load builder ISOs first . compile after save . signal on complete . boot interactive

## Looking for X? Use kind Y

| If you want | Use the kind | Pillar | Already exists? |
|-------------|--------------|--------|-----------------|
| Formal item contract (ID/I/O/owner/acceptance) | builder ISOs (12 per kind) | per-pillar | yes |
| Workflow contract (pre/step/post/error/fallback) | `workflow` or `pipeline_template` | P12 | no -- not in lean distill |
| Quality rubric + threshold + retries | `quality_gate` + `scoring_rubric` + `revision_loop_policy` | P11 + P07 | no -- not in lean distill |
| Memory governance (what/how-long/version/invalidate) | `memory_architecture` + `consolidation_policy` + `lifecycle_rule` | P10 + P11 | no -- not in lean distill |
| Permission layers (create/alter/approve/publish) | `rbac_policy` + `permission` + `role_assignment` | P11 + P02 | yes |
| Audit trail (origin/version/decision/approver) | `audit_log` + `lineage_record` + frontmatter | P11 + P12 | no -- not in lean distill |
| Multi-judge cross-provider review | `crew_template` (process: consensus) + `judge_config` (provider_override) | P12 + P07 | no -- not in lean distill |
| RACI / role boundaries | `.claude/rules/raci-matrix.md` + nucleus_def | rule | yes |
| Risk catalog | `_docs/RISK_CATALOG.md` + `threat_model` kind | P11 | no -- not in lean distill |
| Severity matrix | `.claude/rules/8f-reasoning.md` (Severity Matrix section) | rule | yes |
| Honesty mechanic against sycophancy | F7c COUNCIL sub-step (cross-provider) | rule | yes |
| End-to-end walkthrough | `examples/06_full_lifecycle/` | example | yes |
| Executive summary | `docs/EXECUTIVE_SUMMARY.md` | doc | no -- not in lean distill |
| Canonical glossary | `docs/glossary.md` | doc | no -- not in lean distill |

> **Taxonomy Hygiene Rule**: if you don't see your concept here, apply the 5-question test in `.claude/rules/composable-crew.md` BEFORE proposing a new kind. The 125-kind taxonomy is sufficient -- gaps are usually composition gaps, not category gaps.
