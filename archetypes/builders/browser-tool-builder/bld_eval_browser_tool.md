---
kind: quality_gate
id: p11_qg_browser_tool
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of browser_tool artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: browser_tool"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, browser-tool, P04, playwright, dom, selectors, automation]
tldr: "Pass/fail gate for browser_tool artifacts: engine declaration, action completeness, selector fallback chains, timeout config, and output format con..."
domain: "browser automation tool — DOM-based web interaction with declared engine, actions, selectors, and output contract"
created: "2026-03-28"
updated: "2026-03-28"
8f: "F7_govern"
keywords: [browser automation tool, and output contract, engine declaration, action completeness, selector fallback chains, timeout config, and output format contract]
density_score: 0.90
related:
  - bld_instruction_browser_tool
  - bld_schema_browser_tool
  - browser-tool-builder
  - bld_knowledge_card_browser_tool
  - p11_qg_cli_tool
---
## Quality Gate

# Gate: browser_tool
## Definition
| Field | Value |
|---|---|
| metric | browser_tool artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: browser_tool` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p04_browser_[a-z][a-z0-9_]+$` | ID missing prefix, contains hyphens, or has uppercase |
| H03 | ID equals filename stem | `id: p04_browser_foo` but file is `p04_browser_bar.md` |
| H04 | Kind equals literal `browser_tool` | `kind: scraper` or `kind: tool` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | Engine is a recognized enum value | `engine: browser` or `engine: chrome` or unrecognized string |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Action coverage | 1.0 | All actions in frontmatter have matching body sections |
| Selector fallback | 1.5 | Each element has primary+fallback selectors |
| Engine specificity | 1.0 | Headless, viewport, timeout, JS flag declared |
| Output schema | 1.0 | Field names, types, null handling defined |
| Timeout config | 1.0 | Timeout declared; no unbounded waits |
| Wait strategy | 1.0 | Wait condition per navigate/wait action |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Internal debug tool used only during development; never shipped to production pipelines |
| approver | Author self-certification with comment explaining debug-only scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — debug tools must be promoted to >= 7.0 or removed from repo |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H06 (unrecognized engine makes tool unrunnable) |

## Examples

# Examples: browser-tool-builder
## Golden Example
INPUT: "Create browser tool for scraping product listings from a marketplace"
OUTPUT:
```yaml
id: p04_browser_marketplace_scraper
kind: browser_tool
pillar: P04
version: "1.0.0"
created: "2026-03-28"
updated: "2026-03-28"
author: "builder_agent"
name: "Marketplace Product Scraper"
engine: playwright
actions: [navigate, wait, extract, screenshot]
selectors: [css, xpath, data_attr]
output_format: json
headless: true
viewport: "1280x720"
timeout: 30000
javascript: true
cookies: false
stealth: true
quality: 8.8
tags: [browser_tool, marketplace, scraper, playwright, P04]
tldr: "Playwright scraper for marketplace product listings: navigate, wait for load, extract structured data, screenshot on failure"
description: "Extracts product name, price, rating, and seller from marketplace listing pages using CSS and data-attribute selectors"
user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```
## Overview
Extracts structured product data (name, price, rating, seller, availability) from marketplace
listing pages. Used by price-monitoring pipelines and competitive analysis agents.
Triggers on a list of product URLs; returns one JSON object per URL.
## Engine
Engine: Playwright (chromium). Headless: true. Viewport: 1280x720.
Timeout: 30000ms per action. JavaScript: enabled (required for dynamic content).
Stealth: true — randomized user_agent, navigator.webdriver = false.
## Actions
### navigate
Navigates to URL, waits for networkidle. Params: url (required), waitUntil.
### wait
Waits for product container. Selector: `[data-testid="product-container"]` / `.product-main`.
### extract
Extracts name/price/rating/seller via data_attr with css fallback. Returns JSON; null for missing.
### screenshot
Captures viewport on failure. Params: fullPage (bool), path (string).
## Selectors
Priority: data_attr > aria > css > xpath. Fallback: try next if null.
## Output
```json
{"url":"string","name":"string|null","price":"number|null","rating":"number|null","seller":"string|null","available":"boolean"}
```
WHY GOLDEN: H01-H10 all pass (valid YAML, id pattern, kind, quality:null, all fields, enums, timeout). Soft: selectors w/fallback (S04), output schema (S05), stealth (S06), tldr 119ch (S01), 5 tags (S02). Score ~9.2.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
