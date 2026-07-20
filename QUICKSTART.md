# QUICKSTART

Zero to running in about a minute, then your first brain interaction. Every command below
is verified against this repo's own launcher scripts -- see `start.sh` / `start.ps1` /
`boot/run.sh` / `boot/run.ps1` / `boot/cex.sh` / `boot/cex.ps1`.

## Prerequisites

- **Git**
- **Node.js 18.17+** (both web apps need it -- `apps/public_site`, `apps/dashboard_web`)
- **Python 3.11+** (the vendored `cexai/` brain package this repo installs declares
  `requires-python >= 3.11`; the thinner root `pyproject.toml` floors at 3.10+ but only
  covers `_tools`/`cex_sdk` -- 3.11+ is the real effective floor)
- Optional: **Claude Code CLI** (or Codex / Gemini / Ollama) if you want to talk to the
  brain, not just click through the storefront

## 1. Clone

```bash
git clone https://github.com/GatoaoCubo/cexai-starter.git
cd cexai-starter
```

## 2. Make it yours (optional, recommended -- about 2 minutes)

This starter ships **unfilled**: brand name = "Sua Empresa" (Portuguese for "Your
Company"), every brand-specific field = `[preencher]` ("fill in"). Fill it in now, or skip
this step and explore the unfilled starter first -- you can always come back to it.

```bash
python _tools/cex_bootstrap.py --check
#   -> BOOTSTRAPPED: Sua Empresa   (exit 0 -- confirms the unfilled placeholder)

python _tools/cex_bootstrap.py --reset
#   backs up .cex/brand/brand_config.yaml to *.yaml.bak, restores the blank template,
#   then prints "Brand reset. Run bootstrap again." and exits -- it does NOT auto-prompt

python _tools/cex_bootstrap.py
#   interactive fill: brand name, tagline, values, tone, audience, monetization
#   non-interactive alternative: python _tools/cex_bootstrap.py --from-file your_brand.yaml
```

This fills in the **brain's own identity** (`.cex/brand/brand_config.yaml`), auto-injected
into every nucleus prompt from then on. See [README.md](README.md#make-it-yours-in-2-minutes)
for what this does and does not re-personalize in the running apps.

## 3. Bring the apps up (menu path -- recommended)

```bash
# Mac / Linux / WSL / Git-Bash
sh start.sh

# Windows (PowerShell)
.\start.ps1
```

You get a menu:

```
1) Rodar a VITRINE (site publico)      -> localhost:3000  + abre navegador
2) Rodar o ADMIN (dashboard do tenant) -> localhost:3001  + abre navegador
3) Rodar a API (capacidades)           -> localhost:8000
4) Rodar TUDO (vitrine + admin + API)
5) Abrir a vitrine no navegador (se ja rodando)
0) Sair
```

(The launcher's own menu prints in Portuguese; the actions are: 1 storefront, 2 admin, 3
API, 4 everything, 5 reopen the storefront in your browser, 0 exit.) Pick `4` for the full
experience. First run installs Node dependencies (roughly 1-2 minutes, cached after that).
The storefront opens at `http://localhost:3000/t/starter` -- `starter` is this repo's tenant
slug, already baked into the launcher. It serves fixture data
(`NEXT_PUBLIC_FIXTURES=1`) -- no backend or database required to see it live.

## 4. Manual path (no menu)

Bring up all three apps in one shot with the plain launcher (each app in its own
console/job):

```bash
sh boot/run.sh       # Mac / Linux / WSL
boot/run.ps1          # Windows (PowerShell)
```

Or start a single app by hand:

```bash
cd apps/public_site
npm install
NEXT_PUBLIC_FIXTURES=1 NEXT_PUBLIC_ADMIN_URL=http://localhost:3001 PORT=3000 npm run dev
```

`NEXT_PUBLIC_FIXTURES=1` matters -- without it the storefront looks for a live
`NEXT_PUBLIC_API_URL` backend and fails to load data. Both launcher scripts set this for
you; only set it by hand if you skip them.

The admin (`apps/dashboard_web`) works the same way (`PORT=3001`,
`NEXT_PUBLIC_TENANT=starter`); the API (`apps/dashboard_api`) needs its own Python
dependencies first:

```bash
pip install -r apps/dashboard_api/requirements.txt
python -m uvicorn apps.dashboard_api.main:app --port 8000 --reload
```

## 5. Verify the fabrication

```bash
python _tools/cex_bootstrap.py --check
```

Expected output before you fill it in: `BOOTSTRAPPED: Sua Empresa` (exit code 0) -- that is
the unfilled placeholder name, not an error. After step 2 it reports your own brand name
instead. Run this from THIS repo's root -- a checkout of the upstream factory would resolve
a different (or `unknown`) brand.

## First brain interaction

You have the apps running. Now talk to the brain itself.

### Boot the in-repo AI operator (N07)

```bash
sh boot/cex.sh       # Mac / Linux / WSL
boot/cex.ps1          # Windows (PowerShell)
```

This launches Claude Code pre-loaded as this tenant's N07 orchestrator, with `CLAUDE.md`,
the brand, and all 318 kinds already in context. Needs the `claude` CLI on `PATH`. From
inside that session (or any Claude Code session opened at this repo's root) you get six
commands:

| Command | What it does |
|---|---|
| `/run` | Bring up the 3 local apps (same as step 3 above) |
| `/build <intent>` | Run the full 8F pipeline in-session and produce one artifact |
| `/guide [goal]` | Co-pilot mode -- ask you the subjective decisions before building |
| `/validate` | Health-check every artifact in the tenant (`cex_doctor`) |
| `/mentor [explain\|quiz] <concept>` | Learn the brain -- 8F, kinds, pillars, capabilities |
| `/simplify [path]` | Audit a diff or path for reuse / quality / efficiency |

This tenant is a **solo-operator** brain: one session drives the whole pipeline (no
multi-nucleus dispatch or grid here -- see [AGENTS.md](AGENTS.md) for what that means in
practice).

### Run the health check

```bash
python _tools/cex_doctor.py
```

Scans every artifact in the tenant -- frontmatter, size, density, naming, wiring -- and
exits non-zero on a hard gate failure. The builder-integrity count (`Builders: 316 ... 0
FAIL`) is the headline number; a few advisory MEDIUM findings elsewhere in the check
registry are normal and do not block anything.

### Build one artifact via 8F

```bash
# Dry run first -- no LLM call, shows the pipeline plan
python _tools/cex_8f_runner.py "create a knowledge card about our return policy" \
  --dry-run --verbose

# Real build -- requires an LLM available to your session (Claude Code / API key / Ollama)
python _tools/cex_8f_runner.py "create a knowledge card about our return policy" \
  --execute --verbose
```

`--kind <kind>` skips classification if you already know the target kind; `--nucleus N0X`
targets a specific department. On success, compile and re-check:

```bash
python _tools/cex_compile.py <output_path>
python _tools/cex_doctor.py
```

Your nuclei are departments, not lone agents -- N01-N06 each ship a working crew on top of
the single artifact you just built. Try: `python _tools/cex_crew.py list`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Port `3000`, `3001`, or `8000` already in use | Stop whatever is bound to it, or edit `PORT=` in the relevant launcher command |
| Storefront loads blank / data errors | Confirm `NEXT_PUBLIC_FIXTURES=1` is set -- without it the app looks for a live API and has none in a fresh clone |
| `dashboard_api` never starts | Its Python deps are optional and auto-skipped when absent: `pip install -r apps/dashboard_api/requirements.txt`, including `python-multipart` (FastAPI crashes on form routes without it) |
| `'node'`/`'npm'` not found | Install Node.js 18.17+ from nodejs.org and re-open your shell |
| `cex_bootstrap.py --check` prints the wrong brand or `unknown` | You are running it from a different checkout (the factory itself, or another tenant) -- `cd` into this repo's root first |
| First `npm run dev` is slow | Expected -- first run does `npm install`; every run after is fast |

## What next

| Goal | Where |
|---|---|
| See the full repo map + live-counted stats | [INDEX.md](INDEX.md) |
| Point Claude Code / Codex / Gemini / Ollama at this repo | [AGENTS.md](AGENTS.md) |
| Full capability table + boot/env reference (generated from this tenant's own state) | [COOKBOOK.md](COOKBOOK.md) |
| Contribute a fix or ask for your own fabrication | [CONTRIBUTING.md](CONTRIBUTING.md) |
