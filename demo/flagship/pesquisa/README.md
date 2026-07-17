# Pesquisa (codexa-v2) -- Pesquisa de Mercado E-commerce BR

> Powered by **CEXAI architecture** (300+ kinds, 12 pillars, 8 nuclei).
> Successor to pesquisa-v1 with the fidelity gap closed.

## What this is

A portable agent bundle for **pesquisa de mercado de e-commerce brasileiro**
(Mercado Livre, Shopee, Amazon BR, Magalu, Americanas). Same 12-pillar
fractal CoC architecture as the codexa-v1 pesquisa bundle, refactored with
CEXAI typed artifacts and lifted from `partial ~70% fidelity` to **`full`**.

## What's new in v2

- **3 actions instead of 1**: brave_search (NEW -- SERP enumeration) +
  tavily (NEW -- research context) + firecrawl (KEPT + hardened).
- **Tier router + fallback chain**: graceful degradation per query phase;
  every chain ends at TIER 1 paste (always-free).
- **CRAG-lite + CRITIC**: per-retrieval and post-synthesis quality checks.
- **4 runtime variants** (D6 multi-runtime): Custom GPT FULL, ChatGPT
  Projects ENXUTO, Claude Projects, Gemini Gems.
- **No satellite mascots** (D2): legacy per-agent mascot naming is dropped;
  the agent is referred to by domain (`pesquisa`).

## Competitive frame -- why pesquisa-v2

| Alternative | Strength | Weakness vs codexa-v2 pesquisa |
|-------------|----------|-------------------------------|
| **Perplexity Spaces** | Built-in web grounding, citations | No marketplace-specific extraction; PT-BR queries miss long-tails; no JSON handoff for anuncio agent |
| **ChatGPT Search** (native) | Zero setup, free | No SERP control; anti-bot fails on ML/Shopee; cannot inject 12P discipline |
| **GPT + 1 firecrawl Action** (codexa-v1 pesquisa) | Already shipped | Single action, no failover; no SERP enumeration; user pays full per-scrape; no parallel collection |
| **codexa-v2 pesquisa** | 3-source action stack + tier router + CRAG-lite + 4 runtime variants + CEXAI 12P | Setup overhead: 3 API keys (mitigated -- any 1 unlocks a useful TIER 3 subset; TIER 1 paste always free) |

**Verdict**: pesquisa-v2 wins the comparison ONLY because of the parallel
action stack + tier router. A single-action upgrade would have left v2
marginally above v1 -- below Perplexity Spaces for users without budget.
The 3 providers + router + fallback chain close 95% of the production
backend's capability gap.

## How to use

Pick your runtime and follow the setup guide:

| Runtime | Setup guide | Effort |
|---------|-------------|--------|
| **Custom GPT FULL** (Plus plan) | `SETUP_chatgpt_custom_gpt.md` | ~10 min (12 files + 3 actions + 3 keys) |
| **ChatGPT Projects ENXUTO** (free plan) | `SETUP_chatgpt_projects.md` | ~5 min (5 files; no actions) |
| **Claude Projects** | `SETUP_claude_projects.md` | ~15 min (knowledge tree + MCP wiring) |
| **Gemini Gems** | `SETUP_gemini_gems.md` | ~5 min (knowledge + Gem instructions) |

For users new to the bundle architecture, start with `SETUP_pt-br.md`
(combined legacy guide).

## Bundle structure

```
pesquisa/
  00_instructions.md            <- 8000-char field for Custom GPT Instructions
  knowledge/                    <- 12 P-files (P01..P12) for Custom GPT upload
    P01_knowledge.md ... P12_orchestration.md
  actions/                      <- 3 OpenAPI specs for TIER 3 actions
    firecrawl_action.yaml
    brave_search_action.yaml
    tavily_search_action.yaml
  projects_free/                <- ENXUTO (5 files for ChatGPT Projects)
  claude/                       <- Claude Projects runtime variant
    Project_instructions.md
    knowledge/                  <- mirror of 12 P-files
    .mcp.json                   <- MCP bridge skeleton
  gemini/                       <- Gemini Gems runtime variant
    Gem_instructions.md
    knowledge/
  cexai/                        <- TYPED CEXAI source-of-truth artifacts
                                   (developer reference; not for upload)
  manifest.yaml                 <- metadata + fidelity matrix
  CONVENTION.md                 <- fractal CoC constitution (verbatim)
  CONVENTION_CEXAI_DELTA.md     <- v2 annex (what CEXAI adds)
  README.md                     <- this file
  SETUP_*.md                    <- per-runtime setup guides (5 total)
```

## TIER 3 actions -- get the API keys

| Provider | Get key | Free tier | Use case |
|----------|--------|-----------|---------|
| firecrawl | https://firecrawl.dev -> API Keys | 500 credits/mo | Deep extraction of one URL |
| brave_search | https://api.search.brave.com -> Get Started | 2000 queries/mo | BR-localized SERP per marketplace |
| tavily | https://tavily.com -> Get Free API Key | 1000 queries/mo | Research context (reviews / trends) |

**Don't have all 3 keys?** That's fine. ANY ONE unlocks a useful TIER 3
subset. The tier router gracefully degrades; TIER 1 paste is always
default and always free. ~100 free pesquisas/mo on combined free tiers
(firecrawl-bound) -- 200-300 with the URL scrape cache hits.

## Honest fidelity statement

This bundle is a **standalone agent**. It does NOT have:
- The production backend's parallel retriever (mercado livre API + serper + exa + youtube + reclameaqui + pytrends + E2B vision)
- The 7-stage CRAG pipeline with multi-criteria 7-dim scoring
- The PostgreSQL persistence layer

But it DOES have (recovering ~95% of capability):
- 3 action providers + tier router + fallback chain
- CRAG-lite per-retrieval scoring + CRITIC post-synthesis verification
- Session-scoped URL scrape cache
- Multi-runtime distribution (4 variants from one source)

Read `knowledge/P04_tools.md` and `knowledge/P08_architecture.md` for
the full honesty about what ported vs what degraded.

## Architecture credit

This bundle is part of a 3-bundle codexa-v2 family (pesquisa + anuncio +
imagens). All three are typed using CEXAI's 303-kind taxonomy with the
same fractal CoC convention. The CEXAI architecture provides:

- 303 typed artifact kinds (knowledge_card, agent, prompt_template, ...)
- 12 pillars (P01 knowledge through P12 orchestration)
- 8 nuclei (N00 genesis through N07 admin)
- 8F reasoning pipeline (F1 CONSTRAIN through F8 COLLABORATE)
- Multi-runtime routing (Claude / Codex / Gemini / Ollama)
- Composable crews (WAVE8) for multi-role deliverables

Learn more: the CEXAI repository documents the full architecture.

## Maintenance

Edit the typed artifacts in `cexai/` FIRST. Then propagate to
`knowledge/` (pillar files), `projects_free/`, `claude/`, `gemini/`.
See `CONVENTION_CEXAI_DELTA.md` -> "Maintenance protocol".

## License + credit

Lineage: codexa-v2 (the original codexa-gpt-bundles 12P architecture).
Powered by CEXAI architecture.
