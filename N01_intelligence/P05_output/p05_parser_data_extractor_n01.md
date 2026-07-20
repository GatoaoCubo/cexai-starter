---
id: p05_parser_data_extractor_n01
kind: parser
pillar: P05
nucleus: n01
title: "N01 Structured Data Extractor"
version: 1.0.0
created: 2026-04-17
author: n01_intelligence
domain: research-intelligence
quality: null
tags: [parser, data_extraction, structured_intelligence, n01, llm_extraction, competitive_data]
tldr: "LLM-powered structured data extractor for N01: transforms raw research text into typed intelligence structures (CompetitorProfile, MarketSignal, PricingData). Outputs match the type_def schema in p06_td_n01.md."
keywords: [llm extraction, data extractor, target_type, schema, extraction prompt, validated]
density_score: 0.89
updated: "2026-04-17"
related:
  - p06_td_n01
  - p04_cli_research_pipeline_n01
  - p03_ch_research_pipeline_n01
  - kc_research_methods
---

## Purpose

Raw source text is unstructured. Intelligence is structured data that can be
compared, ranked, and indexed.

This extractor bridges the two: takes raw text, applies LLM extraction,
outputs typed structures defined in `p06_td_n01.md` (see also the input
contract in `p06_is_n01.md`).

## Target Structure Types

| Type | Fields Extracted | Source Examples |
|------|----------------|----------------|
| CompetitorProfile | name, products, pricing, headcount, funding, strengths, weaknesses | pricing page, professional network, public filings |
| PricingData | tiers, prices, billing_period, free_tier, enterprise | pricing page |
| MarketSignal | signal_type, entity, value, date, confidence | news, financial data |
| ResearchFinding | claim, confidence, sources, counter_evidence | synthesis output |
| HiringSignal | company, roles, count, growth_rate, domain | job postings |
| AcademicPaper | title, authors, year, abstract, citations, key_findings | papers |

## Extraction Pipeline

```
raw_text = DocumentChunk.content
target_type = determine_target_type(chunk.source_url, chunk.title)
prompt = build_extraction_prompt(raw_text, target_type.schema)
result = llm.extract(prompt, output_schema=target_type)
validated = validate(result, target_type.schema)
return validated
```

## Extraction Prompts (by type)

### CompetitorProfile Extraction Prompt

```
Extract a CompetitorProfile from the following text.
Output ONLY valid JSON matching the schema. No prose.

Schema:
{
  "name": "string",
  "products": ["string"],
  "pricing_tiers": [{"name": "string", "price_usd": float, "billing": "monthly|annual"}],
  "free_tier_exists": boolean,
  "headcount_est": int or null,
  "founded_year": int or null,
  "key_differentiators": ["string"],
  "known_weaknesses": ["string"]
}

Text: {raw_text}
```

### PricingData Extraction Prompt

```
Extract all pricing information from the following text.
Return a JSON array of pricing tiers. Be precise with numbers.

Schema per tier:
{"tier_name": str, "price_usd_monthly": float, "price_usd_annual": float or null,
 "seats": str, "key_features": [str], "target_segment": str}

Text: {raw_text}
```

## Validation Rules

| Field | Validation |
|-------|-----------|
| Numeric prices | > 0 and < 100000 (sanity check) |
| Dates | ISO8601 format or null |
| Confidence | 0.0-1.0 |
| Lists | non-empty if present |
| Names | > 2 chars, < 200 chars |

If validation fails: return partial result with `extraction_confidence` = 0.4.
Never hallucinate missing fields -- use null.

## Performance Targets

| Metric | Target |
|--------|--------|
| Extraction accuracy (vs. manual) | > 85% |
| False field fill (hallucination) | < 5% |
| Extraction time per chunk | < 3s |
| Validation pass rate | > 90% |

## Comparison vs. Alternatives

| Approach | Accuracy | Speed | Structured? | N01 Fit |
|----------|---------|-------|-------------|---------|
| Manual extraction | 99% | very slow | yes | impractical |
| Regex / rules | 60% | fast | yes | brittle |
| This (LLM extraction) | 85%+ | medium | yes | optimal |
| Fine-tuned extractor | 95% | fast | yes | future state |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_td_n01]] | upstream | 0.40 |
| [[p04_cli_research_pipeline_n01]] | upstream | 0.36 |
| [[p03_ch_research_pipeline_n01]] | related | 0.32 |
| [[kc_research_methods]] | upstream | 0.26 |
