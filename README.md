<p align="center">
  <img src="docs/assets/cexai-logo.svg" width="280" alt="CEXAI logo">
</p>

<h1 align="center">CEXAI Sovereign Starter</h1>

<p align="center">
  <strong>A complete, sovereign AI brain -- unfilled by design. Clone it, run it, make every variable yours.</strong>
</p>

<!-- Counts below are measured directly against this fabricated tree (2026-07-15), not
     copied from Central's own catalog or from a sibling tenant repo at a different vintage.
     Re-measure after you change the brain -- see INDEX.md "How these numbers were counted". -->

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/node-18+-339933?logo=node.js&logoColor=white" alt="Node">
  <img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="License">
  <img src="https://img.shields.io/badge/LLMs-Claude%20%7C%20GPT%20%7C%20Gemini%20%7C%20Ollama-8A2BE2" alt="LLMs">
  <img src="https://img.shields.io/badge/pillars-12-orange" alt="Pillars">
  <img src="https://img.shields.io/badge/nuclei-8-crimson" alt="Nuclei">
  <img src="https://img.shields.io/badge/kinds-318-red" alt="Kinds">
  <img src="https://img.shields.io/badge/builders-316-brightgreen" alt="Builders">
  <img src="https://img.shields.io/badge/tools-134-informational" alt="Tools">
  <img src="https://img.shields.io/badge/status-UNFILLED%20starter-lightgrey" alt="Unfilled starter">
</p>

<p align="center">
  <img src="docs/assets/hero.png" alt="CEXAI Sovereign Starter" width="720">
</p>

<p align="center">
  <strong>Want a guided, paid course instead?</strong> <a href="https://go.hotmart.com/A106743966I?src=github-readme">Método CEXAI Driver</a> walks through this exact brain, step by step, in Portuguese.
</p>

## What this is

This is an **unfilled, complete, runnable** AI-brain repository: 8 nuclei, 12 pillars, 318
typed artifact kinds, an 8-function reasoning pipeline (8F), and a storefront + admin
dashboard + API already wired to that brain's capability registry. It runs today, out of
the box -- but every brand-specific variable is left **open on purpose**: `[preencher]`
("fill in" in Portuguese) placeholders and the neutral tenant name **Sua Empresa** ("Your
Company") stand in for your name, tagline, colors, contact details, and catalog. This is
the *open-variables principle* -- the brain treats your brand as a template variable, never
a hardcoded fact, so nothing needs to be replaced in code, only filled in config.

This repository was born from the closed CEXAI factory -- the `/genesis` fabrication
service. The factory itself is **not here**: it is not part of this repository and is not
sold as software. What you have here is its **output**: a sovereign, complete copy of the
brain the factory produces, carrying its own git history, phoning home to nobody, ready for
you (or your own AI) to fill in and extend.

## Why this matters if you build agents

Most "AI agent" repos ship a system prompt and a few tools. This one ships a **typed
knowledge system** -- the same one CEXAI itself runs on:

| What you get | Where to look |
|---|---|
| An 8-function reasoning pipeline (F1 CONSTRAIN -> F8 COLLABORATE) that every artifact passes through | `.claude/rules/8f-reasoning.md` |
| 318 typed artifact kinds (knowledge cards, prompts, agents, quality gates, ...) across 12 pillars | `.cex/kinds_meta.json`, `N00_genesis/P01_knowledge/library/kind/` |
| 8 nuclei -- one AI department per business function, each a full 12-pillar fractal | `N00_genesis/` .. `N07_admin/` |
| A runnable storefront + admin + API wired to the brain's own capability registry | `apps/public_site`, `apps/dashboard_web`, `apps/dashboard_api` |
| Multi-runtime brain: the same knowledge system runs on Claude, GPT, Gemini, or a local Ollama model | `.cex/config/nucleus_models.yaml` |
| A solo-operator command set (`/run`, `/build`, `/guide`, `/validate`, `/mentor`, `/simplify`) so one developer -- human or AI -- can drive the whole thing | `.claude/commands/` |

Read it as a reference architecture, run it as a starting point, or fill it in and ship it.

## See it filled

This starter ships unfilled -- but the same brain, fully populated for a real business,
looks like this:

<p align="center">
  <img src="docs/assets/gallery/brain.png" alt="The typed knowledge brain" width="360">
  <img src="docs/assets/gallery/sovereignty.png" alt="Sovereign -- self-hosted, phones home to nobody" width="360">
</p>

That is a **filled** fabrication: the 6 domain nuclei (N01-N06) producing typed
artifacts in parallel under N07's orchestration, a live storefront and admin dashboard wired
to real brand tokens, and every `[preencher]` replaced with a real company's own facts. Want
that, without doing the fill yourself? See
[Want it filled FOR you?](#want-it-filled-for-you) below.

## Make it yours in 2 minutes

The fastest path from "unfilled starter" to "your brand" is the brain's own bootstrap tool,
`_tools/cex_bootstrap.py`. Verified against this exact tree:

```bash
# 1. Confirm what you're looking at (the unfilled placeholder)
python _tools/cex_bootstrap.py --check
#   -> BOOTSTRAPPED: Sua Empresa   (exit 0)

# 2. Clear it: backs up .cex/brand/brand_config.yaml to *.yaml.bak, restores the
#    blank template, then exits -- it does NOT re-prompt automatically
python _tools/cex_bootstrap.py --reset
#   -> "Brand reset. Run bootstrap again."   (exit 0)

# 3. Fill it -- interactively...
python _tools/cex_bootstrap.py
# ...or non-interactively from a YAML file you prepare yourself
python _tools/cex_bootstrap.py --from-file your_brand.yaml

# 4. See it
sh start.sh          # Mac / Linux / WSL / Git-Bash
.\start.ps1          # Windows (PowerShell)
```

Pick option `4` (everything) in the menu. That fills in the **brain's own identity**
(`.cex/brand/brand_config.yaml`, auto-injected into every nucleus prompt from then on). The
storefront's own generated sample content (`apps/public_site/lib/tenantData.generated.ts`)
and the admin's design tokens are a separate, build-time layer -- fully re-personalizing the
running apps (colors, catalog, hero copy) end to end is exactly what the factory's
`/genesis` service does in one pass; see
[Want it filled FOR you?](#want-it-filled-for-you).

## 60-second run

```bash
git clone https://github.com/GatoaoCubo/cexai-starter.git
cd cexai-starter

# Mac / Linux / WSL / Git-Bash
sh start.sh

# Windows (PowerShell)
.\start.ps1
```

A menu comes up -- pick `4` to run the storefront, the admin, and the API together. The
storefront opens automatically at `http://localhost:3000/t/starter` (this starter's tenant
slug is `starter`; the launcher already has it baked in). First run installs Node
dependencies (roughly 1-2 minutes); every run after that is instant.

Full walkthrough, first brain interaction, and troubleshooting: [QUICKSTART.md](QUICKSTART.md).

## What's inside

| Layer | Where | What it is |
|---|---|---|
| Storefront | `apps/public_site` | Public site -- catalog, blog, B2B page, the `/intake` tell-us-about-your-business form |
| Admin | `apps/dashboard_web` | Tenant dashboard -- content, leads, capability runs |
| API | `apps/dashboard_api` | FastAPI backend for the capabilities (ads, pricing, research, lead gen, and more) |
| Typed AI brain | `N00_genesis/` .. `N07_admin/`, `archetypes/builders/`, `cexai/` | 318 kinds, 316 builders, 12 pillars, 8 nuclei, the 8F pipeline -- the same knowledge system that builds CEXAI itself |
| Operating cookbook | [COOKBOOK.md](COOKBOOK.md) | Generated from this tenant's own emitted state -- boot commands, capability table, knowledge map, quality gates. Never a static template; every section names its own source |
| Repo map + live-counted stats | [INDEX.md](INDEX.md) | Where everything lives, counted for real |
| Point-your-agent-here guide | [AGENTS.md](AGENTS.md) | How Claude Code / Codex / Gemini / Ollama should read this repo |

Each `N0X_*` nucleus is a **department**, not just an identity: a pre-filled identity kit
(rules, machine identity, capability card, domain vocabulary), a working **crew** -- role-bound
agents with a handoff protocol (N01-N06; N07 orchestrates the other 6 instead of running its
own) -- and every working pillar (P03-P07, P09, P11, P12) carrying 1-3 exemplar artifacts,
`{{open_vars}}` standing in for anything brand-specific. `N00_genesis/` is the complete mold
with every schema. Full anatomy + the crew table:
[HOME.md](HOME.md#anatomy-each-nucleus-is-a-department).

Based on CEXAI (Apache-2.0) -- see [License](#license) below.

## Want it filled FOR you?

Filling every `[preencher]` by hand works -- but the CEXAI factory can do it for you in one
fabrication run, the same `/genesis` service that produced this starter. Open an issue:

**[github.com/GatoaoCubo/cexai-starter/issues/new?title=I%20want%20my%20own%20sovereign%20repo&body=Company%3A%20%0ASite%3A%20%0AIndustry%3A%20](https://github.com/GatoaoCubo/cexai-starter/issues/new?title=I%20want%20my%20own%20sovereign%20repo&body=Company%3A%20%0ASite%3A%20%0AIndustry%3A%20)**

with your company name, site, and industry -- you get the next steps back. This starter's
own storefront also runs a richer, in-app equivalent at `/intake`
(`apps/public_site/app/intake/`): a 3-persona form (founder, commercial, operations) that
captures the same facts and can download a ready-to-resolve answers file client-side, the
same hybrid mechanism behind `/genesis`.

## Em português (resumo)

Este é o **CEXAI Sovereign Starter**: um cérebro de IA soberano e **completo**, porém **não
preenchido** de propósito -- 8 núcleos, 12 pilares, 318 tipos de artefato, o pipeline de
raciocínio 8F, e uma vitrine + admin + API já conectados ao registro de capacidades do
cérebro. Toda variável de marca fica em aberto ([preencher] / o nome neutro "Sua Empresa")
até você preencher com os dados da sua própria empresa.

**Para rodar**: `sh start.sh` (Mac/Linux/WSL/Git-Bash) ou `.\start.ps1` (Windows) -- um menu
para subir a vitrine, o admin, a API, ou tudo de uma vez, com o navegador abrindo sozinho.
Guia completo: [QUICKSTART.md](QUICKSTART.md).

**Para preencher com a sua marca**: `python _tools/cex_bootstrap.py --reset` e depois
`python _tools/cex_bootstrap.py` (interativo) ou `--from-file sua_marca.yaml`.

**Quer que a fábrica preencha para você?** Abra um issue em
[github.com/GatoaoCubo/cexai-starter/issues/new](https://github.com/GatoaoCubo/cexai-starter/issues/new)
com o nome da sua empresa, site e segmento.

## Every placeholder is yours to fill

Nothing in this starter is fictional -- there is no invented brand, no sample testimonial,
no "amostra" flag anywhere in its data. Every brand-specific value is instead an explicit,
grep-able placeholder: `[preencher]`, or the neutral name **Sua Empresa**. The tenant config
this starter ships with says so directly (`.cex/brand/tenant_config.json`, quoted verbatim,
source is PT-BR):

> "Este e o STARTER SOBERANO (sovereign) da CEXAI: um molde NEUTRO e NAO PREENCHIDO. Toda a
> marca, paleta, textos e o business_shape aqui sao placeholders [preencher] ou um default de
> demonstracao -- nao ha nenhuma historia de empresa real ou ficticia. Para usar: rode o
> bootstrap (python _tools/cex_bootstrap.py, ou python _tools/cex_tenant_bootstrap.py
> --source <sua-URL-ou-PDF-ou-logo> --tenant <seu-slug> --execute --persist-config) sobre a
> SUA marca -- isso substitui cada [preencher] pelos seus dados reais e deriva o seu
> business_shape de verdade."
>
> (translation: "This is CEXAI's sovereign STARTER: a NEUTRAL, UNFILLED template. Every
> brand, palette, copy, and business_shape value here is a `[preencher]` placeholder or a
> demo default -- there is no real or fictional company story. To use it: run the bootstrap
> ... over YOUR brand -- that replaces every placeholder with your real data and derives
> your real business shape.")

Note: the quoted `cex_tenant_bootstrap.py` command is not present in this starter's
`_tools/` (it is a Central-only tool, not carried into the lean distill) -- the verified,
shipped re-fill path is `cex_bootstrap.py`, documented above under
[Make it yours in 2 minutes](#make-it-yours-in-2-minutes).

`[preencher]` appears wherever a brand fact belongs and none has been supplied yet: the
tagline, the archetype, the logo, the hero subline, the blog category, the B2B "who we
serve" line, and every contact field (phone, email, address, WhatsApp, Instagram). Replace
them through the bootstrap flow above, not by hand-editing JSON.

## License

Apache-2.0 -- see [`LICENSE`](LICENSE) (the full text ships in this repository; keep it).
[`NOTICE`](NOTICE) credits the open-source patterns absorbed by the engine that fabricated
this repository (spec-kit, swarms, agno, goose, and others -- pattern-only, no third-party
code vendored). [`TRADEMARK.md`](TRADEMARK.md) is explicit: this fork may say "based on
CEXAI", but the CEXAI name and marks are not licensed by Apache-2.0 -- they are not this
repo's identity, they belong to CEXAI.

---

*CEXAI Sovereign Starter -- unfilled by design, yours by the time you're done reading this.*
