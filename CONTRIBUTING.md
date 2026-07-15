# Contributing

This repo is a **fabricated, unfilled starter tenant** (see [README.md](README.md)), not
the CEXAI engine. That shapes what a contribution here looks like -- lighter scope than
contributing to an engine repo, but real fixes are genuinely welcome.

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## What's welcome

- **Bug fixes** in the apps (`apps/public_site`, `apps/dashboard_web`,
  `apps/dashboard_api`) -- a broken route, a fixture bug, a bad env default.
- **Doc fixes** -- a wrong command, a stale count, a broken link, a clarification.
  `README.md`, `QUICKSTART.md`, `INDEX.md`, `AGENTS.md`, and `COOKBOOK.md` all describe
  *this specific checkout*; if you find a command that does not match reality, that is a
  real bug, please report or fix it.
- **Small corrections inside the brain** (`N00_genesis/` .. `N07_admin/`,
  `archetypes/builders/`) -- a typo, a broken internal link, a factual error in a
  knowledge card.
- **Issues and discussions** -- questions, bug reports, and requests for your own
  fabrication (see below) are all welcome, any time.

## What's out of scope here

- **New capabilities, new kinds, or structural brain changes.** This brain was fabricated
  by the CEXAI factory (the `/genesis` service), not hand-built. Large changes belong
  upstream, in the factory -- not as a hand-edited diff in a fabricated starter. If you
  want a capability this tenant does not have, that is a fabrication request (see below),
  not a PR.
- **Rebranding this repo as something other than a starter of your own.** See
  [TRADEMARK.md](TRADEMARK.md) -- you may fork and fill it in for your own use, but this
  exact repo stays CEXAI's fabricated starter.
- **Fabricating brand facts to replace `[preencher]`.** Do not hand-invent a tagline,
  archetype, logo, or contact detail and hardcode it into this repo's files as if it were
  the shipped default. Every placeholder is meant to be filled by *you*, via
  `python _tools/cex_bootstrap.py` (see [README.md](README.md#make-it-yours-in-2-minutes)),
  never invented on someone else's behalf inside a shared PR.

## First fix in 5 minutes

```bash
git clone https://github.com/GatoaoCubo/cexai-starter.git
cd https://github.com/GatoaoCubo/cexai-starter
sh start.sh                      # or .\start.ps1 on Windows -- confirm it still runs
python _tools/cex_bootstrap.py --check   # confirm: BOOTSTRAPPED: Sua Empresa
```

Make your change, then validate:

```bash
python _tools/cex_doctor.py      # brain artifacts: must not introduce new FAILs
```

If you touched an app (`apps/*`), run its own test suite if one exists (`npm run test`
inside `apps/public_site` or `apps/dashboard_web`; `pytest` inside `apps/dashboard_api` if
you installed its Python deps).

## Quality bar for brain-artifact PRs

| Rule | Why |
|---|---|
| `quality: null` stays in frontmatter | This tenant never self-scores; a peer review or `cex_score.py` assigns the number |
| `python _tools/cex_doctor.py` does not introduce a new FAIL | Repo-wide structural gate |
| No non-ASCII in `.py` / `.ps1` / `.sh` files | `.claude/rules/ascii-code-rule.md` -- Windows terminal + cross-platform compatibility |
| PT-BR content (knowledge cards, brand copy) keeps its accents | Only *code* is ASCII-only; content is not |
| Do not fabricate data | No invented stats, brand facts, or prices -- unresolved facts stay `[preencher]` |

## Asking for your own fabrication

Not a code contribution, but the most common reason people open an issue here: you want a
repo like this one, filled in for **your** company instead of left as `[preencher]`.

**[Open an issue](https://github.com/GatoaoCubo/cexai-starter/issues/new?title=I%20want%20my%20own%20sovereign%20repo&body=Company%3A%20%0ASite%3A%20%0AIndustry%3A%20)**
with your company name, site, and industry. You will get the next steps back. This
starter's own storefront also runs a richer, in-app equivalent at `/intake`.

## Security

There is no dedicated security-disclosure file in this fabrication yet. For a sensitive
finding, do not post secrets, tokens, or personal data in a public issue -- use GitHub's
private vulnerability reporting on this repo if it is enabled, or flag it generically and
a maintainer will follow up privately.

## Questions

Open a **GitHub Discussion** (or an issue, if this repo has discussions disabled) -- not a
PR, for questions.
