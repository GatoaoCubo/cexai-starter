# Changelog

All notable changes to this repository are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## starter v1.1.0 (2026-07-16)

The starter is now a full structural mirror of the CEXAI catalog -- the complete
factory floor, still unfilled by design.

### Added

- **Full kind registry**: 318 kinds in `.cex/kinds_meta.json` (was 125).
- **318 builders** in `archetypes/builders/` (was 119), 12 ISO files each, and
  **318 builder sub-agents** in `.claude/agents/`.
- **All 12 pillar folders in every nucleus** (was 3-4): un-built pillars carry a
  README naming their purpose and example kinds; they fill as your builds write.
- **2 commands** (`/monitor`, `/spec`) whose dependencies fully ship in this tree.

### Changed

- `HOME.md`, `README.md`, `INDEX.md`, `QUICKSTART.md`, `CLAUDE.md` re-counted
  against the real tree and the Anatomy narrative updated to the complete mirror.

## starter v1.0.0 (2026-07-15)

First public version of this fabricated starter tenant repository.

### Added

- **Fabricated from the CEXAI closed factory** via the `/genesis` service -- a sovereign
  copy of the typed AI brain (125 kinds, 119 builders, 12 pillars, 8 nuclei), a storefront,
  an admin dashboard, and an API, generated in a single command, shipped **unfilled** by
  design.
- **Public-facing doc set** -- this repository's own `README.md` (English-first, with a
  condensed Portuguese section), plus `QUICKSTART.md`, `INDEX.md`, `AGENTS.md`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and this `CHANGELOG.md`, mirroring the shape of
  CEXAI's own public-facing documentation, adapted for an unfilled starter rather than a
  fabricated demo or the engine.
- **`/intake` funnel** on the storefront -- a 3-persona form (founder, commercial,
  operations) that captures your brand facts and downloads a ready-to-resolve answers file
  client-side, the same hybrid mechanism behind `/genesis`. A separate, dev-only `/onboard`
  route wires a pasted site URL straight into the tenant bootstrap.

### Changed

- **Engine-clean surface** -- the emitted brain excludes every closed-factory internal
  (family-exclusion + vocabulary scrub + doctor-gate strip + internal index drop), so
  nothing in this repository leaks the factory's own recipe.
- **Factory-skill exclusion** -- the `genesis` / `cexai-factory` recipe skills are removed
  from both skill mirrors (`.claude/skills/`, `.cex/skills/`); this tenant can read and
  extend its own brain, but cannot re-run the closed factory from inside itself.

### Honesty

- Every brand-specific value in this starter is an explicit, grep-able `[preencher]`
  placeholder, or the neutral tenant name **Sua Empresa** -- never an invented fact. The
  tenant config carries its own `_demo_note` disclosing that this is CEXAI's sovereign,
  unfilled starter template. See
  [README.md](README.md#every-placeholder-is-yours-to-fill).
