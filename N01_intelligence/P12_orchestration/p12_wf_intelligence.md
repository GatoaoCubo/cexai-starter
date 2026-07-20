---
id: p12_wf_intelligence
kind: workflow
pillar: P12
nucleus: n01
title: "N01 Workflow -- Research Pipeline"
version: 1.0.0
created: 2026-03-31
author: n01_intelligence
domain: research-intelligence
step_count: 8
quality: null
tags: [workflow, n01, research, pipeline, triangulation]
tldr: "8-step research pipeline: brief -> scope -> search -> triangulate -> synthesize -> format -> validate -> deliver."
keywords: [depth levels, triangulation, quality_gate, signal_writer]
density_score: 0.93
related:
  - p03_ch_research_pipeline_n01
  - p03_pt_research_brief
  - p11_qg_research_n01
  - p12_ct_research_sprint
---

# N01 Workflow -- Research Pipeline

## Pipeline

```
BRIEF -> SCOPE -> SEARCH -> TRIANGULATE -> SYNTHESIZE -> FORMAT -> VALIDATE -> DELIVER
```

| Step | Action | Input | Output | Reference |
|------|--------|-------|--------|------|
| 1 | Receive research brief | User/nucleus request | Classified brief | intent resolver |
| 2 | Scope research | Brief + brand context | Depth level (L1/L2/L3), source plan | depth-level classification |
| 3 | Search sources | Scope + queries | Raw findings (10-50 sources) | `p04_cli_research_pipeline_n01.md` |
| 4 | Triangulate | Raw findings | Verified claims (3+ sources each) | `p06_td_n01.md` (evidence_state field) |
| 5 | Synthesize | Verified claims | Structured analysis | `p03_ch_research_pipeline_n01.md` Step 4 |
| 6 | Format | Analysis | Output template filled | `p03_pt_research_brief.md` |
| 7 | Validate | Formatted output | Quality check (freshness, citations) | `p11_qg_research_n01.md` |
| 8 | Deliver | Validated output | Signal + handoff | signal writer |

## Research Depth Levels

| Level | Time | Sources | Output |
|-------|------|---------|--------|
| L1 Scan | 5 min | 3-5 web | Quick snapshot, bullet points |
| L2 Analysis | 15 min | 10-20 mixed | Structured report with grids |
| L3 Deep-Dive | 30+ min | 20-50 multi-type | Full dossier with projections |

## Anti-Patterns

| Never Do | Why | Instead |
|----------|-----|---------|
| Search before scoping | Wastes time on irrelevant sources | Always classify brief depth (L1/L2/L3) first |
| Single-source claims | Creates unverified intelligence | Require 3+ sources per claim minimum |
| Skip triangulation | Amplifies misinformation | Cross-verify every finding before synthesis |
| Mix raw data with analysis | Confuses facts with interpretation | Separate findings (Step 4) from synthesis (Step 5) |
| Deliver without freshness check | Provides outdated intelligence | Validate recency in Step 7 quality gate |

## Decision Points

| Step | Scenario | Decision | Action |
|------|----------|----------|--------|
| 2 | Brief too vague ("research competitors") | Scope clarification needed | Ask for specific verticals, regions, metrics |
| 2 | Time constraint vs depth requested | L3 brief but 10min available | Negotiate down to L2 or extend timeline |
| 3 | Paywall sources blocking research | Premium content inaccessible | Shift to academic papers, company reports, public filings |
| 4 | <3 sources found for key claim | Triangulation impossible | Flag as "single-source claim" and note confidence level |
| 4 | Sources contradict each other | Conflicting information | Present both views with source attribution |
| 6 | Multiple output formats requested | Format selection unclear | Use the research brief template unless specifically requested |
| 7 | Sources >6 months old | Freshness gate failure | Re-search with date filters or flag as historical analysis |
| 8 | Handoff target unclear | Delivery ambiguity | Signal the orchestrator and await routing instructions |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ch_research_pipeline_n01]] | upstream | 0.36 |
| [[p03_pt_research_brief]] | upstream | 0.34 |
| [[p11_qg_research_n01]] | upstream | 0.32 |
| [[p12_ct_research_sprint]] | related | 0.30 |
