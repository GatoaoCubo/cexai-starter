---
quality: null
id: p01_kc_mcp_config_hygiene
kind: knowledge_card
kc_type: ops_kc
pillar: P01
nucleus: N04
version: 1.0.0
created: "2026-06-11"
updated: "2026-06-11"
author: n04_knowledge
title: "MCP Config Hygiene -- Example Pattern, Gitignore, Validator"
domain: ops
subdomain: mcp_config
tags: [mcp, gitignore, secrets, setup, hygiene, example-pattern, cex_setup_validator]
tldr: "The live .mcp.json holds machine-specific paths and API key env refs -- it must never be committed. Keep a .mcp.json.example (tracked) with placeholder values; add .mcp.json to .gitignore; let cex_setup_validator warn fresh clones to copy-and-fill."
when_to_use: "When onboarding a new machine, wiring MCP servers, or auditing secret hygiene in the repo."
keywords: [mcp.json, gitignore, example-pattern, cex_setup_validator, fresh-clone, api-key, placeholder]
density_score: null
related:
  - p01_kc_model_context_protocol
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_setup_validator. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

## Why the Example Pattern

`.mcp.json` contains two machine-specific concerns that must NEVER land in git:

| Concern | Example value | Risk if committed |
|---------|--------------|-------------------|
| Absolute node path | `C:\\Program Files\\nodejs\\npx.cmd` | Breaks every machine with a different Node install location |
| API key env refs | `${GITHUB_PAT}`, `${FIRECRAWL_API_KEY}` | If a contributor expands these before committing, real tokens leak |

The fix is the **example-pattern**: track `.mcp.json.example` (generic placeholders, no secrets) and gitignore the live `.mcp.json`.

## The Three-Layer Contract

| Layer | File | Action |
|-------|------|--------|
| Tracked template | `.mcp.json.example` | Ships with repo; placeholders like `<YOUR_GITHUB_PAT>` |
| Gitignored live config | `.mcp.json` | Each developer copies the example and fills in real values |
| Validator gate | `cex_setup_validator.py` (MCP_SERVERS) | WARNs (INFO) if `.mcp.json` absent while `.mcp.json.example` exists |

## Gitignore Rule

```
# Live root MCP config (machine-specific paths + keys -- copy from .mcp.json.example)
.mcp.json
```

The per-nucleus overlays (`.mcp-n01.json` etc.) were already covered by `.mcp-n*.json`.
The root `.mcp.json` needs its own explicit entry because the glob does not match it.

## Setup Validator Behavior

When `cex_setup_validator.py` runs (category `MCP_SERVERS`):

| Condition | Output |
|-----------|--------|
| `.mcp.json` present | `[OK] .mcp.json present (configured)` |
| `.mcp.json` absent, `.mcp.json.example` exists | `[--] .mcp.json absent -- copy .mcp.json.example and fill in values` |
| Both absent | `[--] .mcp.json absent (MCP servers optional)` |

The check is INFO (non-fatal) because MCP servers are optional. A fresh clone still passes the validator.

## Fresh-Configure Flow

<!-- [N02 narrative sweep 2026-07-15, DP_B]: tenant repo readers already hold
     the code; the private engine repo is unreachable by design. Removed the
     "clone the engine" step. -->
**You already have step 1.** This tenant repo is the clone -- sovereign,
pre-fabricated, and the private engine behind it stays closed forever, so no
`git clone` is needed. Pick up at step 2 below.

```bash
# 2. Copy the example
cp .mcp.json.example .mcp.json

# 3. Fill in your values
#    - Replace <YOUR_GITHUB_PAT> with a real PAT (repo read scope)
#    - Replace <YOUR_FIRECRAWL_API_KEY> if you use web scraping
#    - Replace Canva keys if you use the Canva MCP
#    - Leave disabled:true for servers you don't need

# 4. Validate
python _tools/cex_setup_validator.py  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
# Expect: [OK] .mcp.json present (configured)
```

## Anti-Patterns

| Anti-pattern | Consequence |
|--------------|-------------|
| Commit real `.mcp.json` with expanded keys | Secret leak in git history |
| Commit `.mcp.json` with hardcoded paths | Every collaborator's Node path breaks |
| Skip `.mcp.json.example` | Fresh clones have no guidance; MCP stays unconfigured |
| Put real tokens in `.mcp.json.example` | Example is tracked -- tokens leak immediately |

## Related

- p04_mcp_server -- MCP server kind builder (P04)
- [[p01_kc_model_context_protocol]] -- MCP protocol KC
- `_tools/cex_setup_validator.py` -- check_mcp_hygiene() and check_mcp_servers()  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
- `.mcp.json.example` -- the tracked template
