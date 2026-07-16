---
id: kc_nucleus_def
kind: knowledge_card
8f: F3_inject
title: "CEX Nucleus Definition (N00-N07): The nucleus_def Kind"
version: 1.1.0
quality: null
pillar: P01
domain: architecture
subdomain: nucleus_identity
author: n04_knowledge
created: "2026-04-14"
updated: "2026-06-06"
tldr: "How to read and author a nucleus_def: the machine-readable identity card for a CEX nucleus (N00-N07) -- role, sin lens, owned pillars, model tier, boot + agent-card paths."
when_to_use: "Load when defining, referencing, or routing to a nucleus identity. Consult for: what is N0x's role/sin lens, and which fields does a nucleus_def carry?"
keywords: [nucleus_def, nucleus, bounded_context, sin_lens, pillars_owned, boot_script, agent_card, cli_binding, fractal]
long_tails:
  - "what role and sin lens does each CEX nucleus N01-N07 have"
  - "how do I author a nucleus_def and which fields are required"
tags: [knowledge_card, nucleus_def, identity, bounded-context, fractal, P02, teaching]
density_score: 1.0
related:
  - nucleus_def_n01
  - nucleus_def_n03
  - nucleus_def_n04
---

# CEX Nucleus Definition (N00-N07)

A `nucleus_def` (kind, pillar P02, 8F verb CONSTRAIN) is the machine-readable
identity card for one CEX nucleus. In DDD terms each nucleus is a **bounded
context**: its own language, rules, and owned pillar. The card makes the fractal
explicit -- it is what the orchestrator and the prompt compiler read to route work
to the right nucleus.

## The Eight Nuclei

Each row is grounded in the live `nucleus_def_n0x.md` files under
`N0x_*/P02_model/`. The "sin lens" is the optimization bias the nucleus
applies (the Seven Sins map in `CLAUDE.md`).

| Nucleus | Role | Sin Lens | Primary Pillar | Directory |
|---------|------|----------|----------------|-----------|
| N00 | genesis (archetype source) | none (root) | all 12 (P01-P12) | `N00_genesis/` |
| N01 | intelligence | Analytical Envy | P01 knowledge | `N01_intelligence/` |
| N02 | marketing | Creative Lust | P03 prompt | `N02_marketing/` |
| N03 | engineering | Inventive Pride | P05 output / P06 schema | `N03_engineering/` |
| N04 | knowledge | Knowledge Gluttony | P01 knowledge / P10 memory | `N04_knowledge/` |
| N05 | operations | Gating Wrath | P07 evals / P09 config | `N05_operations/` |
| N06 | commercial | Strategic Greed | P11 feedback | `N06_commercial/` |
| N07 | orchestrator | Orchestrating Sloth | all 12 (dispatch) | `N07_admin/` |

Note: the 12 pillars are a fractal -- EVERY nucleus mirrors all 12 pillar
directories. "Primary Pillar" above is the domain a nucleus leads; it does not
own the others exclusively (Clean-Arch dependency rule: pillars depend inward,
never the reverse).

## nucleus_def Schema (the fields a card carries)

From `.cex/kinds_meta.json` (`nucleus_def`, naming `nucleus_def_{{nucleus_id_lower}}.md`,
max_bytes 5120):

| Field | Meaning |
|-------|---------|
| `nucleus_id` | N00..N07 |
| `role` | the domain the nucleus leads (e.g. intelligence) |
| `sin_lens` | the optimization bias (e.g. Analytical Envy) |
| `pillars_owned` | list of pillars this nucleus leads |
| `cli_binding` | runtime CLI (claude / gemini / codex / ollama) |
| `model_tier` | opus / sonnet / haiku |
| `boot_script` | e.g. `boot/n01.ps1` |
| `agent_card_path` | A2A capability declaration path |
| `crew_templates_exposed` | crews this nucleus can run |
| `domain_agents` | the agents it spawns |

## How to Use
You are an agent reading or authoring a nucleus identity. Use this card to:

1. **Route** -- given an intent, read the `role` column to pick the nucleus
   (research -> N01, build -> N03, deploy -> N05; see `n07-orchestrator.md`).
2. **Reference** -- when a handoff names a nucleus, resolve its `boot_script`,
   `agent_card_path`, and `sin_lens` from its `nucleus_def_n0x.md`.
3. **Author** -- to create a new nucleus_def, copy `nucleus_def_n01.md` as the shape,
   fill every schema field above, set `quality: null`, and place it at
   `N0x_*/P02_model/nucleus_def_n0x.md`. Bootstrapping N08+ is governed by
   `.claude/rules/new-nucleus-bootstrap.md` (pick a sin lens, scaffold 12 pillars).

Never invent a sin lens or role -- they are fixed by the Seven-Sins map. Never
collapse two nuclei into one bounded context; if a domain already exists, extend it.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[nucleus_def_n01]] | instance | 0.50 |
| [[bld_knowledge_nucleus_def]] | builder | 0.46 |
| [[nucleus_def_n03]] | instance | 0.44 |
| [[nucleus_def_n04]] | instance | 0.43 |
| component_map_n01 | downstream | 0.40 |
