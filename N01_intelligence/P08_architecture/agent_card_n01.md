---
id: p02_card_intelligence
kind: agent_card
8f: F2_become
pillar: P02
title: "N01 Research Analyst — Agent Card"
version: 4.0.0
created: 2026-03-31
author: n07_orchestrator
domain: research-intelligence
quality: null
tags: [agent_card, n01, research, analyst, routing]
tldr: "Research Analyst routing card — 12 capabilities, hybrid provider, input/output contracts, inter-nucleus handoffs."
keywords: [competitive grid, market snapshot, trend report, source dossier, swot analysis, benchmark report, executive summary, web grounding, deep synthesis]
density_score: 0.93
related:
  - p02_agent_intelligence_n01
  - n01_dr_intelligence
  - n01_intelligence
  - component_map_n01
  - n01_dr_research_pipeline
---

# N01 Research Analyst — Agent Card

## Routing
- **Priority**: 8 (high — research often precedes other nuclei)
- **Keywords**: research, competitor, market, trend, analyze, benchmark, compare, investigate, SWOT, pricing, who, what's happening, industry
- **Dispatch**: `Task tool: dispatch solo n01 "task"`

## Provider
| Mode | Provider | When |
|------|----------|------|
| Search | Gemini 2.5 Pro | Web grounding, large docs |
| Analysis | Claude | Deep synthesis, nuance |
| Fallback | Either | Rate limit on primary |

## Capabilities Map

| Capability | Input | Output Template |
|-----------|-------|-----------------|
| Competitive Grid | competitors list + dimensions | output_competitive_grid.md |
| Market Snapshot | category + geography | output_market_snapshot.md |
| Trend Report | domain + timeframe | output_trend_report.md |
| Source Dossier | topic + depth level | output_source_dossier.md |
| SWOT | company/product | output_swot_analysis.md |
| Benchmark | products + criteria | output_benchmark_report.md |
| Executive Summary | any research output | output_executive_summary.md |

## Anti-Patterns (Route AWAY)

| Don't Use For | Route To Instead | Why |
|---------------|------------------|-----|
| "Write marketing copy for X" | N02 | Creative writing, not research |
| "Build me a landing page" | N03 | Artifact creation, not analysis |
| "Debug this code" | N05 | Technical operations |
| "Create a knowledge card" | N04 | Knowledge management |
| "Set up pricing for course" | N06 | Commercial strategy |

## Inter-Nucleus Handoffs

| From | To N01 | What |
|------|--------|------|
| N06 | Competitor research request | "Research these 5 competitors" |
| N07 | Mission decomposition | "Research phase of /plan" |
| N02 | Design benchmark | "Find UI patterns in category X" |

| From N01 | To | What |
|----------|-----|------|
| Research complete | N06 | Competitive positioning data |
| Trend report | N04 | New KC material |
| Benchmark | N02 | Design reference data |

## Composable Crews

| Crew | Process | Roles | Purpose |
|------|---------|-------|---------|
| competitive_intelligence | sequential | 3 (analyst, synthesizer, validator) | Peer-reviewed competitive intelligence brief with source verification |
| deep_research | sequential | 4 (scout, analyst, fact_checker, writer) | Comprehensive fact-validated research report with confidence scoring |
| trend_analysis | sequential | 3 (scanner, pattern_detector, brief_writer) | Emerging trend detection with temporal signal clustering and momentum scores |
| source_verification | sequential | 3 (harvester, cross_checker, confidence_scorer) | Standalone source validation layer -- reusable across any artifact |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p02_agent_intelligence_n01 | related | 0.37 |
| n01_dr_intelligence | downstream | 0.36 |
| [[n01_intelligence]] | downstream | 0.36 |
| component_map_n01 | downstream | 0.36 |
| n01_dr_research_pipeline | downstream | 0.35 |
