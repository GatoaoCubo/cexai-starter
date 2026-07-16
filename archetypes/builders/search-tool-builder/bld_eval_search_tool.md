---
kind: quality_gate
id: p11_qg_search_tool
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of search_tool artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: search_tool"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, search-tool, P04, web-search, semantic-search, provider]
tldr: "Pass/fail gate for search_tool artifacts: provider specification, max_results, result structure, cost documentation, and API key security."
domain: "Web, semantic, and hybrid search tools that connect LLM agents to external search services"
created: "2026-03-28"
updated: "2026-03-28"
8f: "F7_govern"
keywords: [provider specification, result structure, cost documentation, and api key security, quality-gate, search-tool, web-search]
density_score: 0.90
related:
  - search-tool-builder
---
## Quality Gate

# Gate: search_tool
## Definition
| Field | Value |
|---|---|
| metric | search_tool artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: search_tool` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p04_search_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or no p04_search_ prefix |
| H03 | ID equals filename stem | ID does not match filename |
| H04 | Kind equals literal `search_tool` | `kind: search` or `kind: tool` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `provider`, `search_type`, or `max_results` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Provider documentation | 1.0 | Provider name, API endpoint pattern, authentication method |
| Result field clarity | 1.0 | Each result field has type and description |
| Cost documentation | 1.0 | cost_per_query with calculation example |
| Rate limit awareness | 1.0 | rate_limit documented with throttle strategy |
| Filtering options | 0.5 | Date range, domain filter, language support documented |
| Query documentation | 1.0 | Query parameters with types, defaults, examples |
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
| conditions | Internal test search tool for development |
| approver | Author self-certification with test-only scope comment |
| audit_trail | Bypass note in frontmatter with expiry date |
| expiry | 14d — test tools must be promoted or removed |
| never_bypass | H01 (unparseable YAML), H05 (self-scored gates), H09 (hardcoded API keys = security risk) |

## Examples

# Examples: search-tool-builder
## Golden Example
INPUT: "Create search tool for Tavily AI-optimized web search"
OUTPUT:
```yaml
id: p04_search_tavily_web
kind: search_tool
pillar: P04
version: "1.0.0"
created: "2026-03-28"
updated: "2026-03-28"
author: "builder_agent"
name: "Tavily Web Search"
provider: "tavily"
search_type: web
max_results: 10
result_fields:
  - title
  - url
  - content
  - score
date_range: true
domain_filter: true
language: ["en", "pt", "es"]
cost_per_query: "~$0.005"
rate_limit: "100/min"
quality: 8.8
tags: [search_tool, tavily, web-search, ai-optimized, P04]
tldr: "Tavily AI web search: 10 results, clean text content, date/domain filters, $0.005/query"
description: "AI-optimized web search via Tavily API returning clean text results for LLM consumption"
```
## Overview
AI-optimized web search via Tavily API. Returns clean, LLM-ready text content instead of raw HTML.
Use when agent needs current web information with high-quality, pre-processed text results.
## Query
### Parameters
- `query` (string, required): natural language search query
- `max_results` (integer, optional, default: 10): results to return (1-20)
- `search_type` (enum, optional): "web" (default) or "news"
### Filtering
- Date range: supported — filter by recency (day, week, month, year)
- Domain filter: supported — include/exclude specific domains
- Language: en, pt, es supported
## Results
### Structure
Each result contains:
- `title` (string): page title
- `url` (string): source URL
- `content` (string): cleaned text content (not raw HTML)
- `score` (float): relevance score 0-1
### Ranking
Results ranked by Tavily relevance algorithm optimized for LLM consumption.
### Pagination
No cursor-based pagetion — adjust max_results parameter.
## Provider
- API: api.tavily.com/search
- Auth: env var `TAVILY_API_KEY` (NEVER hardcode)
- Rate limit: 100 requests/minute
- Cost: ~$0.005 per query ($5/1000 queries)
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p04_search_ pattern (H02 pass)
- kind: search_tool (H04 pass)
- provider: "tavily" specified (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
