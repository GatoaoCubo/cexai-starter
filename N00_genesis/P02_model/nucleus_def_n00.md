---
id: nucleus_def_n00
kind: nucleus_def
8f: F2_become
primary_8f: F2_become
pillar: P02
nucleus: N00
nucleus_id: N00
role: genesis
title: "N00 Genesis -- Nucleus Definition"
version: "1.2.0"
created: "2026-04-27"
updated: "2026-07-05"
quality: null
density_score: 0.92
domain: "archetype"
sin_lens: null  # archetype, no sin
cli_binding: reference-only
model_tier: none
model_specific: n/a
context_tokens: 0
boot_script: n/a
agent_card_path: N00_genesis/P08_architecture/agent_card_n00.md
pillars_owned:
  - P01
  - P02
  - P03
  - P04
  - P05
  - P06
  - P07
  - P08
  - P09
  - P10
  - P11
  - P12
crew_templates_exposed: []
domain_agents: []
fallback_cli: n/a
tldr: "Machine-readable identity contract for N00 Genesis -- the pre-sin archetype the router BECOMEs when resolving the structural template for all nuclei."
when_to_use: "Load when cex_router / boot scripts need N00's identity, or when scaffolding a new vertical (N08+) from the archetype. Consult for N00's scope + quality contract."
keywords: [nucleus_def, n00, genesis, archetype, identity, BECOME, routing, sin-lens, P02]
long_tails:
  - "what is the N00 genesis nucleus and when is it used"
  - "how do I read a nucleus identity contract for routing"
related:
  - agent_card_n00
  - kc_nucleus_def
  - nucleus-def-builder
tags:
  - nucleus_def
  - n00
  - identity
---

# N00 Genesis -- Nucleus Definition

Machine-readable identity contract for N00 GENESIS. Loaded by `cex_router.py`,
`cex_dispatch`, and per-nucleus boot scripts. Maps a nucleus's role to its
operational scope, sin lens, and quality contract.

> **Consolidation note (2026-07-05):** this file merges the two historical
> `nucleus_def_n00.md` copies (register row R-027). Canonical path is
> `P02_model/` per `.claude/rules/new-nucleus-bootstrap.md` (9-asset table) and
> `_tools/cex_new_nucleus.py::render_nucleus_def()` (both independently name
> `P02_model` as the nucleus_def home for every nucleus, present and future).
> The former `P08_architecture/nucleus_def_n00.md` copy is removed (content
> lives on here + in git history). Field provenance: `cli_binding`,
> `model_tier`, `model_specific`, `context_tokens`, `pillars_owned`,
> `crew_templates_exposed`, `domain_agents`, and the Pillars Owned / Crew
> Templates Exposed / Domain Agents / Boot Contract / Composability sections
> below come from the removed P08_architecture copy (its own `id:` field read
> `p02_nd_n00.md`, a stray naming artifact from genesis -- discarded in favor
> of this file's `nucleus_def_n00` id, which matches its filename and every
> sibling nucleus_def). Everything else is this file's pre-existing content.

> **Second fix pass (2026-07-05, register rows R-098/R-101):** the merge above
> carried two live defects forward from the removed P08_architecture copy
> unexamined. Both are fixed in this pass: (1) `pillars_owned: [P00]` cited a
> pillar that does not exist in the 12-pillar system (P01-P12 only) -- corrected
> to the full P01-P12 list, since N00 is structurally the only nucleus that owns
> ALL 12 pillars (it is the schema/manifest source every N01-N07 + every tenant's
> F1 CONSTRAIN reads from, not a 2-4-pillar domain specialist like an operational
> nucleus). (2) `agent_card_path` pointed at `N00_genesis/agent_card_n00.md`,
> which never existed (confirmed absent via `find`, also flagged independently
> in `docs/NUCLEUS_ARCHITECTURE_DOSSIER.md`'s N00 card) -- the card is now
> created at `N00_genesis/P08_architecture/agent_card_n00.md` (matching the
> convention every other nucleus's agent_card follows post R-024/R-025) and this
> path is repointed to match.

### How to use this contract

```text
ROLE: you are the router/boot resolving a nucleus identity (8F: F2 BECOME).
You must read this contract before adopting the N00 archetype persona.
1. Read the Identity table -> adopt nucleus_id, domain, pillar.
2. Apply the Sin Lens -- N00 is PRE-SIN; do not instantiate it for production.
3. Honor the Quality Contract (publish >= 8.0, self-scoring NEVER).
4. For a new vertical, COPY this shape and fill the slots below per N08+.
```

Identity slots (filled per nucleus when cloning the archetype):

```text
<NUCLEUS_ID>     # e.g. n08
<DOMAIN>         # the vertical's domain (healthcare, fintech, ...)
<SIN_LENS>       # one of the seven sins (N00 itself is null/pre-sin)
<PILLAR>         # the definition pillar (P02 for a nucleus_def)
```

## Identity

| Field | Value |
|-------|-------|
| **Nucleus ID** | `n00` |
| **Full name** | N00 Genesis |
| **Domain** | archetype |
| **Sin lens** | Pre-sin archetype |
| **Pillar (definition)** | P02 (Model) |
| **CLI binding** | reference-only (never spawned) |
| **Model tier** | none |
| **Context** | n/a |

## Sin Lens

N00 has no sin. It is the pre-sin archetype: the structural template from which all sin-driven nuclei (N01-N07) inherit. Never instantiated for production work; serves as source-of-truth for pillar schemas, kind library, and 12-ISO builders.

## Operational Scope

This nucleus owns work in the **archetype** domain. Tasks routed here when:

- Bootstrap workflow needs the archetype template
- A new community vertical (N08+) is being scaffolded
- 8F structural defaults need to be referenced

## Pillars Owned

N00 is the only nucleus that owns **all 12 pillars** at once. Every N01-N07
(and every distilled tenant) picks 2-4 *primary* pillars for its own domain
work, but reads ALL 12 of N00's `_schema.yaml` files at F1 CONSTRAIN regardless
-- N00 is the schema/manifest substrate underneath every nucleus, not a domain
specialist (see `component_map_n00.md` for the live per-pillar kind-manifest
count; corrected from a stale `pillars_owned: [P00]` -- P00 does not exist --
register row R-101).

| Pillar | Domain | Sample Kinds |
|--------|--------|--------------|
| P01 | Knowledge | knowledge_card, rag_source, citation |
| P02 | Model | agent, nucleus_def, model_provider |
| P03 | Prompt | prompt_template, system_prompt, chain |
| P04 | Tools | mcp_server, browser_tool, api_client |
| P05 | Output | landing_page, pitch_deck, press_release |
| P06 | Schema | input_schema, type_def, validator |
| P07 | Evals | benchmark, scoring_rubric, llm_judge |
| P08 | Architecture | agent_card, component_map, decision_record |
| P09 | Config | env_config, rate_limit_config, feature_flag |
| P10 | Memory | entity_memory, knowledge_index, procedural_memory |
| P11 | Feedback | quality_gate, guardrail, content_monetization |
| P12 | Orchestration | workflow, crew_template, dispatch_rule |

## Crew Templates Exposed

_None_ -- N00 is reference-only.

## Domain Agents

_None_ -- no spawnable agents. N00 is the source data.

## Quality Contract

| Aspect | Value |
|--------|-------|
| Min score to publish | 8.0 |
| Target score | 9.0+ |
| Self-scoring | NEVER (peer review only) |
| 8F mandatory | YES |

## Boot Contract

_Not applicable_ -- N00 is never spawned. Other nuclei READ N00 as reference.

## Related Files

- **Agent card**: [N00_genesis/P08_architecture/agent_card_n00.md](../P08_architecture/agent_card_n00.md)
- **Component map**: [N00_genesis/P08_architecture/component_map_n00.md](../P08_architecture/component_map_n00.md)
- **Boot script (Windows)**: n/a (never spawned)
- **Per-nucleus rule**: `N00_genesis/rules/n00-genesis.md` (N07 reads its own: `.claude/rules/n07-orchestrator.md`)

## Composability

| Direction | Nucleus | What Flows |
|-----------|---------|-----------|
| outbound | all N01..N07 | schemas, archetypes, kinds registry |
| inbound | none | N00 does not accept inputs |

## Routing Hints

This nucleus answers when the user intent maps to:
- **Used as**: archetype reference (not direct dispatch)

See `.claude/rules/n07-input-transmutation.md` for the full verb-to-nucleus mapping.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| n07-orchestrator | upstream | 0.85 |
| [[agent_card_n00]] | sibling (capability declaration) | 0.80 |
| component_map_n00 | sibling (inventory) | 0.55 |
| [[kc_nucleus_def]] | upstream | 0.38 |
| [[nucleus-def-builder]] | related | 0.33 |
| 8f-reasoning | foundational (F2 BECOME) | 0.55 |
