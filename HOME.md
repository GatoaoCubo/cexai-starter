---
title: CEXAI Sovereign Starter
description: A sovereign, unfilled AI brain -- 318 kinds, 318 builders, 12 pillars, 8 nuclei. Navigate the real architecture, not a diagram of it.
---

# CEXAI Sovereign Starter

**A complete, sovereign AI brain -- unfilled by design.** Clone it, run it, make every
variable yours.

This is not "an open-source engine." The factory that fabricated this repository (the
closed `/genesis` service) is not here and is not for sale -- what you have is its
**output**: a full, typed knowledge system with its own git history, phoning home to
nobody. Read [[README|README.md]] for the full pitch, or keep reading -- this page is the
front door into the graph you are looking at right now.

> Every link on this page, and every node in [[architecture|the architecture canvas]],
> resolves to a real file in the tree you cloned. Nothing here is illustrative-only --
> click through and you are reading the actual repo.

## In numbers (measured against this exact checkout, 2026-07-15)

| Kinds | Builders | Pillars | Nuclei | Tools | Docs |
|---:|---:|---:|---:|---:|---:|
| **125** | **119** | **12** | **8** | **88** | **10** |

- **Kinds** -- typed artifact categories, `.cex/kinds_meta.json`: `python -c "import json; print(len(json.load(open('.cex/kinds_meta.json', encoding='utf-8'))))"`
- **Builders** -- `archetypes/builders/*-builder/` (12 ISO files each): `ls archetypes/builders | grep -c -- '-builder$'`
- **Pillars** -- P01..P12, the domain taxonomy every nucleus mirrors (fixed by design, not counted)
- **Nuclei** -- N00 (archetype) + N01..N07 (operational): `ls -d N0*_*/ | wc -l`
- **Tools** -- Python CLIs, `_tools/*.py`: `ls _tools/*.py | wc -l`
- **Docs** -- the 8 root guides + 2 `docs/` references published on this page (the exact
  set in [[INDEX|INDEX.md]]'s repo map): `README, QUICKSTART, INDEX, AGENTS, CONTRIBUTING,
  CHANGELOG, CODE_OF_CONDUCT, COOKBOOK` + `docs/HYDRATION_MAP.md`, `docs/RUNTIME_ANY_MODEL.md`

These are the same counts [[README|README.md]] and [[INDEX|INDEX.md]] already publish --
re-verified against this checkout while building this page, not copied from a template or
from CEXAI's own (much larger) engine repo. If you change the brain, re-run the commands
above; nothing here auto-updates.

## The 8 nuclei -- one department per business function

Each nucleus is a full 12-pillar knowledge department: its own knowledge, prompts, tools,
schemas, evals, architecture, config, memory, feedback, and orchestration folders.

| Nucleus | Domain | Sin lens | Rules (identity) | Machine identity |
|---|---|---|---|---|
| N00 Genesis | archetype -- template for the rest | -- | [[N00_genesis/rules/n00-genesis\|n00-genesis.md]] | [[N00_genesis/P02_model/nucleus_def_n00\|nucleus_def_n00.md]] |
| N01 Intelligence | research | Analytical Envy | [[N01_intelligence/rules/n01-intelligence\|n01-intelligence.md]] | [[N01_intelligence/P02_model/nucleus_def_n01\|nucleus_def_n01.md]] |
| N02 Marketing | marketing / brand | Creative Lust | [[N02_marketing/rules/n02-marketing\|n02-marketing.md]] | [[N02_marketing/P02_model/nucleus_def_n02\|nucleus_def_n02.md]] |
| N03 Engineering | build / construction | Inventive Pride | [[N03_engineering/rules/n03-builder\|n03-builder.md]] | [[N03_engineering/P02_model/nucleus_def_n03\|nucleus_def_n03.md]] |
| N04 Knowledge | knowledge base | Knowledge Gluttony | [[N04_knowledge/rules/n04-knowledge\|n04-knowledge.md]] | [[N04_knowledge/P02_model/nucleus_def_n04\|nucleus_def_n04.md]] |
| N05 Operations | quality / ops | Gating Wrath | [[N05_operations/rules/n05-operations\|n05-operations.md]] | [[N05_operations/P02_model/nucleus_def_n05\|nucleus_def_n05.md]] |
| N06 Commercial | monetization | Strategic Greed | [[N06_commercial/rules/n06-commercial\|n06-commercial.md]] | [[N06_commercial/P02_model/nucleus_def_n06\|nucleus_def_n06.md]] |
| N07 Admin | orchestration (identity) | Orchestrating Sloth | [[N07_admin/rules/n07-admin\|n07-admin.md]] | [[N07_admin/P02_model/nucleus_def_n07\|nucleus_def_n07.md]] |

*This starter is a solo-operator brain, not a multi-agent dispatch grid: `/build` runs the
8F pipeline in-session, one operator at a time. All 8 nuclei above are real and
addressable -- read a rules file, or ask your agent to "act as N02" -- you just do it
yourself, rather than fanning work out to parallel processes. Full explanation:
[[AGENTS|AGENTS.md]] ("This is a solo-operator brain").*

## The 8F reasoning pipeline

Every artifact this brain produces passes through the same eight functions, whether it is
a knowledge card, a prompt template, or an agent:

```
F1 CONSTRAIN -> F2 BECOME -> F3 INJECT -> F4 REASON -> F5 CALL -> F6 PRODUCE -> F7 GOVERN -> F8 COLLABORATE
```

| F | Name | What happens |
|---|---|---|
| F1 | CONSTRAIN | Resolve kind + pillar + schema + limits |
| F2 | BECOME | Load the builder's 12 ISOs, adopt its identity |
| F3 | INJECT | Pull in knowledge cards, examples, brand context |
| F4 | REASON | Plan sections, approach, references |
| F5 | CALL | Line up tools, check for reusable artifacts |
| F6 | PRODUCE | Generate the complete artifact |
| F7 | GOVERN | Validate gates, score quality (never self-scored) |
| F8 | COLLABORATE | Save, compile, signal completion |

Full protocol and the worked "5 words in -> professional artifact out" example: see the
8F section of [[INDEX|INDEX.md]]. Run it yourself: `python _tools/cex_8f_runner.py
"<intent>" --dry-run --verbose`.

## The 12 pillars -- domain taxonomy every nucleus mirrors

| Pillar | Domain | Pillar | Domain |
|---|---|---|---|
| P01 | Knowledge | P07 | Evaluation |
| P02 | Model | P08 | Architecture |
| P03 | Prompt | P09 | Config |
| P04 | Tools | P10 | Memory |
| P05 | Output | P11 | Feedback |
| P06 | Schema | P12 | Orchestration |

Every one of the 8 nuclei carries this same 12-pillar taxonomy on disk -- expand any
`N0X_*` folder in the sidebar and all 12 subfolders are there. Pillars you have not
built into yet hold a short README describing what belongs there; the Anatomy section
just below explains the design.

## Anatomy: why nuclei look "incomplete"

Every `N0X_*` nucleus carries all 12 pillar folders. What differs is how much each one
holds on day 1 -- a nucleus ships as an **identity kit**, not a pre-filled department:

| Ships in every nucleus | Lives in |
|---|---|
| Identity + sin lens | `rules/n0X-*.md` |
| Machine-readable identity | `P02_model/nucleus_def_n0X.md` |
| Capability card | `P08_architecture/agent_card_n0X.md` |
| Domain vocabulary | `P01_knowledge/kc_*_vocabulary.md` |

(most nuclei also carry `P10_memory/procedural_memory_n0X.md`, their operating SOPs). Every
other pillar folder holds a short README naming its purpose and example kinds -- a labeled
shelf, ready for your work. The complete 12-pillar mold -- every schema included -- ships as
[[N00_genesis/rules/n00-genesis|N00_genesis]]. A pillar fills the first time your own
`/build` writes into it; until then its README marks the spot. Nothing is missing:
the factory floor is complete, and the shelves are yours to fill.

## Navigate

| If you want... | Go to |
|---|---|
| The full pitch, 60-second run, license | [[README\|README.md]] |
| Numbered setup + first brain interaction | [[QUICKSTART\|QUICKSTART.md]] |
| The repo map + every stat, re-countable | [[INDEX\|INDEX.md]] |
| To point an LLM/agent at this repo | [[AGENTS\|AGENTS.md]] |
| Daily-ops commands, capability table, env vars | [[COOKBOOK\|COOKBOOK.md]] |
| To contribute, or ask for your own fabrication | [[CONTRIBUTING\|CONTRIBUTING.md]] |
| What shipped in this version | [[CHANGELOG\|CHANGELOG.md]] |
| Behavior expectations | [[CODE_OF_CONDUCT\|CODE_OF_CONDUCT.md]] |
| The whole architecture, one glance, visually | [[architecture\|architecture.canvas]] |
| One kind's full contract, worked example | [[N00_genesis/P01_knowledge/library/kind/kc_agent\|kc_agent.md]], [[N00_genesis/P01_knowledge/library/kind/kc_knowledge_card\|kc_knowledge_card.md]], [[N00_genesis/P01_knowledge/library/kind/kc_prompt_template\|kc_prompt_template.md]] |

The full kind registry (all 125, machine-readable) lives at `.cex/kinds_meta.json` and the
complete kind-KC library at `N00_genesis/P01_knowledge/library/kind/` -- both are real,
both ship in your clone; only the individual kind KCs are part of this published graph
(the registry itself is JSON config, not a knowledge page, so it is not published here).

## Make it yours

This starter ships **unfilled**: `[preencher]` placeholders and the neutral tenant name
**Sua Empresa** stand in for your brand everywhere. Fill it yourself in two minutes:

```bash
python _tools/cex_bootstrap.py --check     # confirm you're looking at the unfilled placeholder
python _tools/cex_bootstrap.py             # interactive fill
sh start.sh                                # or .\start.ps1 on Windows -- see it live
```

Full walkthrough: [[QUICKSTART|QUICKSTART.md]]. Every placeholder, and why nothing here is
invented or fictional: [[README|README.md]] ("Every placeholder is yours to fill").

**Want the factory to fill it for you instead?** The same `/genesis` fabrication service
that produced this starter can do the whole pass -- brand, catalog, storefront, admin --
in one run. Open an issue with your company name, site, and industry:

**[Open a "make me one" issue on cexai-starter](https://github.com/GatoaoCubo/cexai-starter/issues/new?title=I%20want%20my%20own%20sovereign%20repo&body=Company%3A%20%0ASite%3A%20%0AIndustry%3A%20)**

## Em português (resumo)

Este e o **CEXAI Sovereign Starter**: um cerebro de IA soberano e completo, porem **nao
preenchido** de proposito -- 8 nucleos, 12 pilares, 125 tipos de artefato, o pipeline de
raciocinio 8F (F1 a F8). Nao e "um motor open-source": a fabrica fechada que gerou este
repositorio (`/genesis`) nao esta aqui -- o que voce tem e a **saida** dela, com historico
git proprio, sem telefonar para ninguem.

**Para rodar**: `sh start.sh` (Mac/Linux/WSL/Git-Bash) ou `.\start.ps1` (Windows).
**Para preencher com a sua marca**: `python _tools/cex_bootstrap.py --reset` e depois
`python _tools/cex_bootstrap.py` (interativo). Guia completo: [[QUICKSTART|QUICKSTART.md]].
**Quer que a fabrica preencha para voce?** Abra o issue linkado acima com o nome da sua
empresa, site e segmento.

---

*Front door generated for this checkout's Obsidian Publish graph. Every count above was
measured, every link was tested against this tree -- see this mission's build report for
the exact verification commands.*

