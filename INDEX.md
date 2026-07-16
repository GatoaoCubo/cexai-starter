# Repo Index

Navigation map for this repo. Read this if you are looking for a specific entry point.
Every count below was taken directly from this checkout (see "How these numbers were
counted" at the bottom) -- not copied from a template.

## Where do I start?

| If you are... | Read first |
|---|---|
| A new visitor deciding if this is useful | [README.md](README.md) -- what this is, why it matters, 60-second run |
| Trying it for the first time | [QUICKSTART.md](QUICKSTART.md) -- numbered commands, "make it yours" step, first brain interaction, troubleshooting |
| An LLM / coding agent booting into this repo | [AGENTS.md](AGENTS.md) -- boot scripts, `CLAUDE.md`, the 8F protocol |
| Looking for daily-ops commands, the capability table, or env vars | [COOKBOOK.md](COOKBOOK.md) -- generated from this tenant's own emitted state |
| Wanting to contribute or ask for your own fabrication | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Checking what shipped in this version | [CHANGELOG.md](CHANGELOG.md) |
| Reporting behavior expectations | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |

## Repo map

```
https://github.com/GatoaoCubo/cexai-starter/
+-- README.md                        -- value prop + 60-second run + "every placeholder is yours to fill"
+-- QUICKSTART.md                    -- numbered setup, make-it-yours step, first brain interaction, troubleshooting
+-- INDEX.md                         -- this file
+-- AGENTS.md                        -- how to point your agent at this repo
+-- CONTRIBUTING.md                  -- contribution scope (docs/fixes; the brain regenerates from the factory)
+-- CODE_OF_CONDUCT.md               -- behavior standard
+-- CHANGELOG.md                     -- versioned history, starts at v1.0.0
+-- COOKBOOK.md                      -- operating cookbook, generated from this tenant's own state
+-- CLAUDE.md                        -- Claude Code runtime entry (auto-loaded)
+-- LICENSE . NOTICE . TRADEMARK.md  -- Apache-2.0 + attribution + naming policy
+-- start.sh / start.ps1             -- one-command menu launcher (storefront / admin / API / all)
|
+-- docs/
|   +-- assets/          -- logo, hero, favicon, gallery/ (this doc set's own media)
|   +-- RUNTIME_ANY_MODEL.md  -- swap the LLM backend behind the native claude CLI
|   +-- HYDRATION_MAP.md      -- knowledge-carry map for this tenant
|
+-- apps/
|   +-- public_site/    -- storefront (Next.js) -- catalog, blog, B2B page, /intake, /onboard
|   +-- dashboard_web/  -- admin dashboard (Next.js) -- content, leads, capability runs
|   +-- dashboard_api/  -- capabilities backend (FastAPI, `main.py`)
|
+-- N00_genesis/                     -- archetype nucleus (12-pillar source of truth)
+-- N01_intelligence/ .. N07_admin/  -- 7 operational nuclei, each a 12-pillar fractal
|
+-- archetypes/builders/  -- 119 typed builders (12 ISO files each)
+-- cexai/                -- the vendored cexai Python package (governance, memory, orchestration, ...)
+-- cex_sdk/              -- Python SDK surface (agent, credentials, models, schema)
+-- _tools/               -- 88 Python CLI tools (cex_doctor, cex_8f_runner, cex_bootstrap, ...)
+-- boot/                 -- launchers: cex.sh/.ps1 (N07), run.sh/.ps1 (3 apps), anymodel/litellm
|
+-- brand/ . overlay/  -- this tenant's identity + enabled-capability overlay (committed, not secret)
+-- .cex/              -- runtime config: kinds_meta.json, nucleus_models.yaml, brand, total_index
+-- .claude/           -- agents, commands, rules, skills (Claude Code surface)
|
+-- docs/ . _docs/      -- reference docs + compiled specs
+-- examples/           -- worked walkthroughs (06_full_lifecycle)
+-- supabase/           -- Postgres/Supabase migrations + RLS tests
+-- .github/workflows/  -- CI (quality, webapp, data-plane gates)
```

## The 8F reasoning pipeline

```
F1 CONSTRAIN -> F2 BECOME -> F3 INJECT -> F4 REASON
                                       -> F5 CALL
                                       -> F6 PRODUCE
                                       -> F7 GOVERN
                                       -> F8 COLLABORATE
```

Every artifact this brain produces passes through all eight functions.
Reference: [`.claude/rules/8f-reasoning.md`](.claude/rules/8f-reasoning.md).
Run it yourself: `python _tools/cex_8f_runner.py "<intent>" --dry-run --verbose`.

## Looking for a kind?

318 kinds spread across 12 pillars. Browse:
[`.cex/kinds_meta.json`](.cex/kinds_meta.json) or
[`N00_genesis/P01_knowledge/library/kind/`](N00_genesis/P01_knowledge/library/kind/).
For "I have concept X, which kind covers it?", see `CLAUDE.md`'s
**Looking for X? Use kind Y** table.

## The 8 nuclei -- departments on the 12-pillar taxonomy

| Nucleus | Domain | Sin lens | Pillars on disk |
|---|---|---|---|
| N00_genesis | archetype (template for the rest) | -- | 12/12 (the complete mold) |
| N01_intelligence | research | Analytical Envy | 12/12 |
| N02_marketing | marketing/brand | Creative Lust | 12/12 |
| N03_engineering | build/construction | Inventive Pride | 12/12 |
| N04_knowledge | knowledge base | Knowledge Gluttony | 12/12 |
| N05_operations | quality/ops | Gating Wrath | 12/12 |
| N06_commercial | monetization | Strategic Greed | 12/12 |
| N07_admin | orchestration | Orchestrating Sloth | 12/12 |

> All 12 pillar folders ship in every nucleus: the identity kit comes pre-filled, the rest hold a README marking what belongs there until your builds fill them. `N00_genesis/` carries every schema. See [HOME -> Anatomy](HOME.md#anatomy-why-nuclei-look-incomplete).

Details, department-vocabulary mapping, and per-nucleus sources:
[COOKBOOK.md](COOKBOOK.md#nuclei-as-departments).

## Stats

| Metric | Count |
|---|---:|
| Artifact kinds | 125 |
| Builders (`archetypes/builders/*-builder/`) | 119 |
| Pillars per nucleus | 12 |
| Nuclei (1 archetype + 7 operational) | 8 |
| Python CLI tools (`_tools/*.py`) | 88 |
| Claude Code builder sub-agents (`.claude/agents/*.md`) | 121 |
| Slash commands (`.claude/commands/*.md`) | 6 |
| Governance rules (`.claude/rules/*.md`) | 10 |
| Lazy-loaded skills (`.claude/skills/*.md`) | 28 |
| Local apps | 3 (storefront, admin, API) |
| CI workflows (`.github/workflows/`) | 3 |
| Supabase migrations | 9 |

## How these numbers were counted

Every count above came from running the equivalent of the commands below against this
exact checkout -- re-run them yourself any time to catch drift:

```bash
python -c "import json; print(len(json.load(open('.cex/kinds_meta.json', encoding='utf-8'))))"   # kinds
ls archetypes/builders | grep -c -- '-builder$'                                                    # builders
ls _tools/*.py | wc -l                                                                              # tools
ls .claude/agents/*.md | wc -l                                                                      # sub-agents
python _tools/cex_doctor.py summary                                                                 # builders + density + wiring
```

No auto-updating stat markers are wired into this tenant's docs (the Central-only
`cex_stats.py` companion tool is not carried into a lean distill) -- these are point-in-time
counts, not a live badge. If you change the brain, re-count.
