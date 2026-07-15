---
id: nucleus_def_n06
kind: nucleus_def
pillar: P02
nucleus: N06
nucleus_id: N06
role: commercial
title: "N06 Commercial -- Nucleus Definition"
version: "1.1.0"
created: "2026-04-27"
updated: "2026-07-07"
quality: null
density_score: 0.92
domain: "pricing/monetization/sales"
sin_lens: "Strategic Greed"
primary_8f: CONSTRAIN
cli_binding: claude
model_tier: sonnet
model_specific: claude-sonnet-4-6
context_tokens: 1000000
boot_script: boot/n06.ps1
agent_card_path: N06_commercial/agent_card_n06.md
pillars_owned:
  - P11
crew_templates_exposed:
  - sales_pipeline
  - pricing_workshop
  - subscription_design
  - partnership_kit
domain_agents: []   # none implemented (R-095, 2026-07-05): agent_pricing_strategist / agent_funnel_optimizer
                    # were removed from this list -- they do not exist on disk and this field is a
                    # structural capability declaration (comments are not machine-visible to any consumer
                    # that parses this list), so leaving them here would keep asserting a false capability.
                    # See "Domain Agents" section below for the honest status + real alternatives.
fallback_cli: gemini
tldr: "Machine-readable identity contract for N06 Commercial -- binds the pricing/monetization/sales nucleus to its scope, sin lens and quality gate -- so the router CONSTRAINs dispatch to the right bounded context."
when_to_use: "Load when the router/boot needs N06's identity. Consult for 'which nucleus owns pricing/monetization/sales and under what quality contract'."
keywords: [nucleus_def, n06, commercial, pricing, monetization, sales, sin_lens, bounded_context, routing]
long_tails:
  - "which nucleus handles pricing and monetization in CEX"
  - "what is the quality contract and sin lens for N06 Commercial"
slots:
  routed_task: "the commercial task being dispatched to N06"
  resolved_verb: "one of: price | monetize | package | target | retain"
related:
  - agent_card_n06
  - n07-orchestrator
  - kc_nucleus_def
tags:
  - nucleus_def
  - n06
  - identity
---

# N06 Commercial -- Nucleus Definition

Machine-readable identity contract for N06 COMMERCIAL. Loaded by `cex_router.py`,
`cex_dispatch`, and per-nucleus boot scripts. Maps a nucleus's role to its
operational scope, sin lens, and quality contract.

> **Consolidation note (2026-07-07):** this file merges the two historical
> `nucleus_def_n06.md` copies (register row R-288, closing the identity-dedup
> family that R-023/R-025/R-026/R-027/R-029 started 2026-07-05 for
> n05/n02/n01/n00/n04). Canonical path is `P02_model/` per
> `.claude/rules/new-nucleus-bootstrap.md` (9-asset table) and
> `_tools/cex_new_nucleus.py::render_nucleus_def()`. The former
> `P08_architecture/nucleus_def_n06.md` copy is removed (content lives on here
> + in git history); its `cli_binding` / `model_tier` / `model_specific` /
> `context_tokens` / `pillars_owned` / `crew_templates_exposed` /
> `domain_agents` fields and its Pillars Owned / Crew Templates Exposed /
> Domain Agents / Boot Contract / Composability sections are folded in below
> (its own `id:` field read `p02_nd_n06.md`, the same stray genesis naming
> artifact discarded for every other nucleus_def -- superseded by this file's
> `nucleus_def_n06` id, which matches its filename). The P08 copy's own
> 2026-07-03 self-review (R-051/R-053/R-095,
> `P08_architecture/self_review_fractal_2026_07_03.md`) had already corrected
> its `context_tokens` (200000 -> 1000000), `fallback_cli` (codex -> gemini),
> and `domain_agents` (removed 2 ghost agents never built, per the
> anti-fabrication policy) -- all 3 corrections ride along with the merge,
> not re-litigated here.

## Identity

| Field | Value |
|-------|-------|
| **Nucleus ID** | `n06` |
| **Full name** | N06 Commercial |
| **Domain** | pricing/monetization/sales |
| **Sin lens** | Strategic Greed |
| **Pillar (definition)** | P02 (Model) |
| **CLI binding** | claude |
| **Model tier** | sonnet (`claude-sonnet-4-6`) |
| **Context** | 1M tokens |
| **Fallback CLI** | gemini |

## Sin Lens

**Strategic Greed** -- this nucleus optimizes for the sin's first word when the task is ambiguous. Two ambiguous goals tie -- sin breaks tie.

## Operational Scope

This nucleus owns work in the **pricing/monetization/sales** domain. Tasks routed here when:

- Pricing models, monetization design
- Brand identity, sales funnels
- Revenue-bias decisions

## Pillars Owned

| Pillar | Domain | Sample Kinds |
|--------|--------|--------------|
| P11 (shared) | feedback | content_monetization |
| P12 (shared) | orchestration | team_charter |

## Crew Templates Exposed

| Template | Roles | Inputs | Outputs |
|----------|-------|--------|---------|
| sales_pipeline | strategist -> content_producer -> closer | team_charter + brand | strategy brief + collateral + closing playbook |
| pricing_workshop | market_analyst -> pricing_architect -> revenue_validator | team_charter + product spec | competitive matrix + tier model + revenue projections |
| subscription_design | segment_researcher -> tier_architect -> retention_analyst | team_charter + customer data | segment profiles + tier model + churn prevention playbook |
| partnership_kit | partner_researcher -> proposal_writer -> deal_reviewer | team_charter + competitive intel | ecosystem map + partner listing + deal governance |

## Domain Agents (Status: NOT IMPLEMENTED, R-095 resolved 2026-07-05)

N06 has **zero** standalone `domain_agent` kind artifacts today (confirmed: `N06_commercial/P02_model/`
holds exactly 6 files -- `agent_commercial.md`, `agent_n06.md`, `axiom_commercial.md`,
`mental_model_commercial.md`, `nucleus_def_n06.md`, `personality_n06.md` -- none is a standalone
`agent_pricing_strategist` or `agent_funnel_optimizer`). The two names below were an aspirational
plan from 2026-04-14 that was never built; per the anti-fabrication policy (never invent capability
to close a gap), this section documents the honest status instead of authoring stub content.

| Planned name (never built) | Intended purpose | Closest REAL alternative today |
|-----------------------------|-------------------|----------------------------------|
| agent_pricing_strategist | Tier + bundle design | `N06_commercial/P12_orchestration/crews/p02_ra_pricing_architect.md` (a `role_assignment` scoped to the `pricing_workshop` crew, not a standalone domain agent -- narrower purpose, different `kind`) |
| agent_funnel_optimizer | Conversion funnel | No equivalent exists. `N06_commercial/P04_tools/funnel_diagnostic_tool.md` is an LLM-driven tool-card spec (F5 CALL step), not an agent |

This is a build-vs-retire decision for a human/founder call, not a mechanical fix: either (a) author
real `domain_agent` artifacts for both names, (b) formally retire the `domain_agents` concept for N06
and rely on the existing crew role_assignments, or (c) redirect `agent_pricing_strategist` to the
`p02_ra_pricing_architect` role_assignment and retire `agent_funnel_optimizer` outright (it has no
close substitute). `domain_agents:` in this file's frontmatter is now `[]` so no tool or LLM reading
this contract is told a capability exists that does not.

## Quality Contract

| Aspect | Value |
|--------|-------|
| Min score to publish | 8.0 |
| Target score | 9.0+ |
| Self-scoring | NEVER (peer review only) |
| 8F mandatory | YES |

## Boot Contract

- Boot file: `boot/n06.ps1`
- Task source: `.cex/runtime/handoffs/n06_task.md`
- Signal: `write_signal('n06', 'complete', {score})`

## Composability

| Direction | Nucleus | What Flows |
|-----------|---------|-----------|
| outbound | N02 | pricing data for copy |
| outbound | N07 | charter gate outcomes |
| inbound | N01 | competitor pricing |
| inbound | N02 | launch copy |

## Related Files

- **Agent card**: [N06_commercial/agent_card_n06.md](../agent_card_n06.md)
- **Boot script (Windows)**: `boot/n06.ps1`
- **Boot script (cross-platform)**: `boot/cex_nucleus.sh n06`
- **Per-nucleus rule**: `.claude/rules/n06-*.md` (N07: `n07-orchestrator.md`)

## Routing Hints

This nucleus answers when the user intent maps to:
- **Verbs**: price, monetize, package, target, retain

See `.claude/rules/n07-input-transmutation.md` for the full verb-to-nucleus mapping.

## Inputs (act-time slots)

The router fills these from the resolved intent tuple before booting N06 (open boundary -- the caller decides, not this contract):

```yaml
slots:
  routed_task: "<the commercial task being dispatched to N06>"
  resolved_verb: "<one of: price | monetize | package | target | retain>"
```

## How to use

You are the router (or a boot script) resolving where commercial work belongs.
This contract is the source of truth for N06's bounded context (DDD: one nucleus = one bounded context).

- Read this card when an intent resolves to `nucleus: n06`; treat its 8F verb as **CONSTRAIN** (it scopes, it does not produce).
- Use the `Routing Hints` verbs to confirm the match before dispatch; never dispatch a non-commercial task here.
- Apply the `Quality Contract` floor (8.0) when gating N06 output -- the gate is the gate.
- Never let N06 score its own artifacts; peer review only.
- Fill the `slots` (`routed_task`, `resolved_verb`) from the resolved intent tuple before boot.

## Procedure

1. Resolve the user intent to `{kind, pillar, nucleus, verb}` via the prompt compiler.
2. Check `nucleus == n06` and the verb is one of price/monetize/package/target/retain.
3. Load this card to confirm domain ownership and the sin lens (Strategic Greed breaks ties).
4. Bind the `slots` (`routed_task`, `resolved_verb`) into the handoff.
5. Dispatch to N06; on completion, gate the artifact against the 8.0 floor via peer review.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| agent_card_n06 | sibling | 0.95 |
| n07-orchestrator | upstream | 0.85 |
| [[nucleus_def_n00]] | upstream | 0.80 |
| [[kc_nucleus_def]] | upstream | 0.42 |
