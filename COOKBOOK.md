# Sua Empresa -- Operating Cookbook

Generated at distill time from this tenant's OWN emitted state (never a static template). A section with no real data source is omitted, never fabricated -- see the `> Source:` footer under each section below.
## Identity

- **Brand**: Sua Empresa
- **Vertical**: services

> Source: `tenant_config.json: brand.name/brand.tagline/shape.vertical (fallback brand_config.yaml: identity.BRAND_NAME/BRAND_TAGLINE)`

## Nuclei-as-Departments

| Nucleus | Department (founder vocabulary) | Sin lens | Pillars present |
|---|---|---|---|
| N01_intelligence | pesquisa (+marketing intel) | Envy | 12/12 |
| N02_marketing | marketing/marca | Lust | 12/12 |
| N03_engineering | construcao (projeto) | Pride | 12/12 |
| N04_knowledge | banco de dados (conhecimento) | Gluttony | 12/12 |
| N05_operations | controle de qualidade (+boot/flags/configs ops) | Wrath | 12/12 |
| N06_commercial | monetizacao | Greed | 12/12 |
| N07_admin | guia da empresa / orquestracao | Sloth | 12/12 |

> Source: `CEXAI_NORTH_STAR.md SS13 crosswalk (static) + a filesystem scan of the emitted <nucleus>/P*_* dirs (which pillars THIS emit actually shipped)`

## Capabilities -- How To Run

Every capability below runs through the shared runtime entry point: `_tools/cex_run_capability.py` -- `run_capability(tenant_id="starter", capability="<slug>", intent=..., credential=...)`.

| Capability | What it does |
|---|---|
| Ads / Copy (`ads`) | Generate brand-voice ad copy and campaign prompt templates -- hooks, CTAs, and platform-length variants for a campaign. |
| Brand Book (`brandbook`) | Build a complete brand book from brand materials (name, essence, logo, colour palette, and any brand text / URL / PDF). Produces 8 structured sections: brand... |
| Competitor Benchmark (`competitor_benchmark`) | Build a competitor benchmark matrix -- rivals scored across the dimensions that matter to your buyer, with sourced cells and a positioning read. |
| Content (`content`) | Capture knowledge / documentation content (a knowledge card) -- RAG-ready docs, internal know-how, and reference material. |
| Knowledge / Docs (`docs`) | Capture and structure knowledge / documentation (a knowledge card) for RAG and doc retrieval. |
| Landing Page (`landing`) | Build a conversion-oriented landing page (responsive, SEO-aware) for a product or offer. |
| Captacao de Leads (`leadgen`) | Find leads around a seed across the available channels (B2C marketplace, B2B CNPJ, UGC social) -- a typed lead list with per-source honest status (ok / block... |
| Marketplace Listing (`marketplace_listing`) | Map a canonical product into a per-channel marketplace listing payload (e.g. Mercado Livre Items API body) + a readiness report (PUBLISH-READY or NOT-READY w... |
| Media / Photo (`media_photo`) | Produce an image / photo BRIEF (a multimodal prompt). The downstream media render (ffmpeg / TTS pipeline) is a separate non-SDK step, out of scope here. |
| OAuth Connect (`oauth_connect`) | Produce a typed OAuth app configuration -- client id/secret slots, scopes, redirect URIs, and token endpoints -- to wire a third-party integration. |
| Pricing (`pricing`) | Design pricing tiers, funnels, and monetization models -- differentiated tiers, feature gating, and revenue framing. |
| Product Docs (`product_docs`) | Capture product documentation as a RAG-ready knowledge card -- features, setup, and how-to reference structured for retrieval. |
| Product Match (`product_match`) | Match a supplier item to a marketplace listing by photo, dimension, and supplier code (EAN excluded on purpose -- every reseller recodes it), with confidence... |
| Research (`research`) | Produce a structured, sourced intelligence brief (a knowledge card). Competitor scans, market research, fact capture. Template-first card. |
| Sourcing Opportunity (`sourcing_opportunity`) | Cross supplier cost (the offer side, parsed from your supplier catalogs) against market price and demand per product type, rank by margin with a skeptical re... |
| Plan Matrix (`tier_designer`) | Design a subscription plan matrix -- differentiated tiers, feature gating, and price anchoring -- as a typed subscription_tier artifact. |

> Source: `plan.selection.caps_enabled (spec 5.4 shape->capability map) + _docs/compiled/cexai_capability_catalog.yaml (label/description)`

## Boot & Daily Ops

- **Bring up the 3 local apps** (public_site :3000, dashboard_web :3001, dashboard_api :8000 -- one console/job each): `boot/run.sh` (Mac/Linux/WSL).
- Windows: `boot/run.ps1` (same 3 apps, each in its own console window).
  - Env vars the launcher sets: NEXT_PUBLIC_BRAND_NAME, NEXT_PUBLIC_FIXTURES, NEXT_PUBLIC_TENANT, PORT
- **Launch the N07 orchestrator** (in-session AI operator): `boot/cex.sh` (Mac/Linux/WSL) or `boot/cex.ps1` (Windows).
  - Env vars the launcher sets: CEX_MODEL_OVERRIDE, CEX_NUCLEUS, CEX_ROOT

> Source: `boot/{cex,run}.{sh,ps1} (existence + env-var tokens grep-verified in the emitted launchers)`

## Knowledge Map

- Kind-KC library: 115 kind KC(s) carried into `N00_genesis/P01_knowledge/library/kind/` (0 scrubbed).
- Self-knowledge: `kc_starter_company.md` (7 real field(s)) in `N00_genesis/P01_knowledge/library/domain/`.
- Procedural memory: 6 nucleus SOP file(s) carried (per-nucleus `P10_memory/procedural_memory_n0X.md`).

- **To add knowledge**: drop a new `kc_*.md` into `N00_genesis/P01_knowledge/library/domain/` (self/company facts) or `library/kind/` (how-to-build-a-kind facts) -- both are scanned by F3 INJECT.

> Source: `manifest.kc_library / manifest.self_kc / manifest.procedural_memory (this distill run's own ledgers)`

## Quality Gates

- Declared gates: `_docs/compiled/distill_verify_gates.yaml` (doctor_status + offline_import_smoke + license_present + kc_library_floor + cookbook_present, run at distill P5 verify).
- Run the health check yourself: `python _tools/cex_doctor.py check`.

> Source: `_docs/compiled/distill_verify_gates.yaml (existence, emitted unconditionally) + plan.selection.tools_kept`

## Improve Loop

- Score an artifact (peer-review, never self-score): `python _tools/cex_score.py <path>`.
- Re-run every quality gate: `python _tools/cex_doctor.py check`.

> Source: `plan.selection.tools_kept (runnability-checked against the emitted lean tool allowlist)`

## Flags / Env Reference

| Variable | Grep-verified in |
|---|---|
| `CEX_MODEL_OVERRIDE` | boot/cex.ps1, boot/cex.sh |
| `CEX_NUCLEUS` | boot/cex.ps1, boot/cex.sh |
| `CEX_ROOT` | boot/cex.ps1, boot/cex.sh |
| `NEXT_PUBLIC_` | apps/dashboard_web/.env.example |
| `NEXT_PUBLIC_API_URL` | apps/dashboard_web/.env.example, apps/public_site/.env.example |
| `NEXT_PUBLIC_BRAND_NAME` | apps/dashboard_web/.env.example, boot/run.ps1, boot/run.sh |
| `NEXT_PUBLIC_BUSINESS_SHAPE` | apps/dashboard_web/.env.example |
| `NEXT_PUBLIC_CEXAI_AUTH` | apps/dashboard_web/.env.example |
| `NEXT_PUBLIC_ENABLE_MANAGEMENT` | apps/dashboard_web/.env.example |
| `NEXT_PUBLIC_FIXTURES` | apps/dashboard_web/.env.example, apps/public_site/.env.example, boot/run.ps1, boot/run.sh |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | apps/dashboard_web/.env.example, apps/public_site/.env.example |
| `NEXT_PUBLIC_SUPABASE_URL` | apps/dashboard_web/.env.example, apps/public_site/.env.example |
| `NEXT_PUBLIC_TENANT` | apps/dashboard_web/.env.example, boot/run.ps1, boot/run.sh |
| `PORT` | boot/run.ps1, boot/run.sh |

> Source: `grep of apps/{public_site,dashboard_web}/.env.example + boot/{cex,run}.{sh,ps1} (the emitted tree; only vars literally present are listed)`
