---
kind: quality_gate
id: p11_qg_parser
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of parser artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: parser"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, parser, P11, P05, governance, data-extraction]
tldr: "Gates for parser artifacts — input format defined, extraction rules tested, output schema matched to consumer."
domain: parser
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.85
related:
  - parser-builder
  - bld_schema_parser
  - bld_architecture_parser
  - p03_ins_parser
  - bld_output_template_parser
---
## Quality Gate

# Gate: parser
## Definition
| Field     | Value                                               |
|-----------|-----------------------------------------------------|
| metric    | extraction rule coverage + output schema fidelity   |
| threshold | 8.0                                                 |
| operator  | >=                                                  |
| scope     | all parser artifacts (P05)                          |
## HARD Gates
All must pass. Failure on any = final score 0.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = parser silently skipped |
| H02 | id matches `^p05_parser_[a-z][a-z0-9_]+$` | Namespace compliance |
| H03 | id == filename stem | Brain search relies on this |
| H04 | kind == "parser" | Type integrity |
| H05 | quality == null | Never self-score |
| H06 | All required fields present: id, kind, pillar, version, created, updated, author, domain, quality, tags, tldr | Completeness |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty | 1.0 |
| S02 | tags is list, len >= 3, includes "parser" | 0.5 |
| S03 | density_score >= 0.80 | 0.5 |
| S04 | Each extraction rule expression tested with a passing sample input in examples block | 1.0 |
| S05 | error_handling block describes strategy for malformed input (skip, default, raise, or partial) | 1.0 |
| S06 | normalization_steps list documents transforms applied after extraction (trim, lowercase, cast, etc.) | 0.5 |
Weights sum: 9.5. Normalize: divide each by 9.5 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as reference parser for this input format |
| >= 8.0 | PUBLISH — wire to ingestion pipeline |
| >= 7.0 | REVIEW — add edge cases, fallback rule, or error handling |
| < 7.0  | REJECT — rework extraction rules and output schema |
## Bypass
| Field | Value |
|-------|-------|
| conditions | One-time migration requiring parser before full validation when input format is stable and small volume |
| approver | p05-chief |
| audit_trail | Log in records/audits/ with input sample, output produced, and timestamp |
| expiry | 48h — parser must pass all gates before production ingestion begins |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples: parser-builder
## Golden Example
INPUT: "Create a parser for extracting product data from marketplace HTML pages"
OUTPUT:
```yaml
id: p05_parser_marketplace_product
kind: parser
pillar: P05
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
input_format: "html"
output_format: "json"
extraction_count: 6
domain: "marketplace_scraping"
quality: null
tags: [parser, marketplace, product, P05, extraction, html]
tldr: "Extracts product title, price, rating, seller, stock, and image from marketplace HTML pages"
error_strategy: "default"
streaming: false
chunking: false
normalization: [trim, lowercase_seller, price_to_float, rating_to_float]
keywords: [marketplace, product, html-parser, price-extraction, scraper-output]
density_score: 0.89
```
## Extraction Rules
| Name | Target | Method | Pattern | Required | Default |
|------|--------|--------|---------|----------|---------|
| title | product_title | css_selector | `h1.product-title` | true | - |
| price | product_price | css_selector | `span.price-current::text` | true | - |
| rating | product_rating | css_selector | `span.rating-value::text` | false | "0.0" |
| seller | seller_name | css_selector | `a.seller-link::text` | true | - |
| stock | stock_status | regex | `(em estoque|esgotado|ultimas unidades)` | false | "unknown" |
| image | image_url | css_selector | `img.product-main::attr(src)` | false | null |
## Input Specification
Format: html
Structure: standard marketplace product page with semantic CSS classes.
Example:
```html
<h1 class="product-title">Kit Decoraction Sala</h1>
<span class="price-current">R$ 149,90</span>
<span class="rating-value">4.7</span>
```
## Output Specification
Format: json
Schema:
```json
{"product_title": "string", "product_price": "float", "product_rating": "float",
 "seller_name": "string", "stock_status": "string", "image_url": "string|null"}
```
## Error Handling
Strategy: default (use default values for optional fields, fail on required).
- On extraction failure (required): raise ParseError with field name and selector
- On extraction failure (optional): use declared default value
- On malformed HTML: attempt partial extraction of available fields
## Normalization
1. trim: remove whitespace from all extracted strings
2. lowercase_seller: normalize seller name to lowercase
3. price_to_float: "R$ 149,90" -> 149.90 (strip currency, swap comma)
4. rating_to_float: "4.7" -> 4.7
WHY THIS IS GOLDEN:
- quality: null (H05) | id p05_parser_ (H02) | kind: parser (H04) | 21 fields (H06)
- extraction_count matches table (H07) | valid enums (H08) | tldr 82ch (S01)

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[parser-builder]] | upstream | 0.47 |
| [[bld_schema_parser]] | upstream | 0.45 |
| [[bld_architecture_parser]] | upstream | 0.42 |
| [[p03_ins_parser]] | upstream | 0.41 |
| [[bld_output_template_parser]] | upstream | 0.38 |
