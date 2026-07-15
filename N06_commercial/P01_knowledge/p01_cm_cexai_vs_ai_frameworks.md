---
id: p01_cm_cexai_vs_ai_frameworks
kind: competitive_matrix
pillar: P01
nucleus: n06
title: "AI Brain Infrastructure -- CEXAI vs AI Frameworks"
version: 1.0.0
created: "2026-06-11"
updated: "2026-06-11"
author: n06_commercial
domain: ai-infrastructure
quality: null
tags: [competitive_matrix, cexai, langchain, crewai, autogen, battle_card]
tldr: "CEXAI vs 5 frameworks on 12 dimensions. Wins: typed governance, self-assimilation, sovereign AI brain. Primary battle: CEXAI vs LangChain."
competitors: [LangChain, CrewAI, AutoGen, DSPy, LlamaIndex]
metrics: [typed_taxonomy, multi_runtime, knowledge_governance, self_assimilation, quality_gates, brand_config, enterprise_sla, implementation_services, sovereign_data, multi_agent, rag_support, license]
analysis_date: "2026-06-11"
key_insights: "Only CEXAI ships 300+ typed kinds + quality gates + self-assimilation -- no competitor governs knowledge permanence."
primary_competitor: LangChain
data_sources:
  - "LangChain docs (docs.langchain.com, 2026-06-11)"
  - "CrewAI docs (docs.crewai.com, 2026-06-11)"
  - "AutoGen docs (microsoft.github.io/autogen, 2026-06-11)"
  - "DSPy (dspy.ai, 2026-06-11)"
  - "LlamaIndex docs (docs.llamaindex.ai, 2026-06-11)"
related:
  - kc_competitive_positioning
  - pitch_deck_intelligence_as_asset
  - p05_lp_cexai_oss_implementation_services
---

# AI Brain Infrastructure -- CEXAI vs AI Frameworks

## Market Context

Segment: Enterprise AI orchestration + knowledge governance.
Scope: Frameworks for AI brain deployment -- NOT narrow task automation.
Analyst: N06 Commercial Nucleus. Date: 2026-06-11.

## Feature Parity Grid

| Capability | CEXAI | LangChain | CrewAI | AutoGen | DSPy | LlamaIndex |
|---|---|---|---|---|---|---|
| Typed artifact taxonomy (300+ kinds) | Yes | No | No | No | No | No |
| Multi-runtime (non-OpenAI native) | Yes | Partial | Partial | No | Yes | Partial |
| 12-pillar architecture | Yes | No | No | No | No | No |
| Self-assimilation loop | Yes | No | No | No | No | No |
| Quality gates (governed outputs) | Yes | No | No | No | Partial | No |
| Brand-configurable per tenant | Yes | No | No | No | No | No |
| Multi-agent crews | Yes | Partial | Yes | Yes | No | No |
| RAG pipeline | Yes | Yes | Partial | Partial | Yes | Yes |
| Enterprise SLA | Yes | No | No | No | No | No |
| Implementation services | Yes | No | No | No | No | No |
| Sovereign data (stays in repo) | Yes | Yes | Yes | Yes | Yes | Yes |
| License | MIT | MIT | MIT | CC-BY-4.0 | MIT | MIT |

Values: Yes / No / Partial / Roadmap Q# YYYY

## Gartner MQ Positioning

| Vendor | Execute (1-5) | Vision (1-5) | Notes |
|---|---|---|---|
| CEXAI | 3 | 5 | Typed governance + services; nascent track record |
| LangChain | 4 | 3 | Ecosystem depth; weak governance; OpenAI-centric |
| CrewAI | 3 | 3 | Strong crews; no knowledge governance |
| AutoGen | 2 | 3 | Research-grade; GPT-4 dependency |
| DSPy | 2 | 4 | Best prompt optimization; narrow scope |
| LlamaIndex | 4 | 3 | RAG leader; limited orchestration |

## Battle Card -- CEXAI vs LangChain

| Dimension | CEXAI | LangChain | Win Reason |
|---|---|---|---|
| Knowledge governance | 300+ types + quality gates | No taxonomy | Permanent assets vs ephemeral chains |
| Multi-runtime | Native fallback chain YAML | Adapters required | Zero-config provider swap |
| Self-improving | Self-assimilation loop | None | Knowledge compounds; LangChain resets |
| Enterprise support | Implementation services + SLA | Community only | Accountability vs DIY |
| Entry cost | Steep (12P + 8F) | Familiar Python | LangChain wins adoption; CEXAI wins depth |

**Anti-FUD:** LangChain claims "100+ LLMs supported." Per docs.langchain.com (2026-06-11): multi-provider requires custom adapters. CEXAI ships tested fallback chains out-of-the-box.

## Pricing Comparison

| Vendor | Entry | Enterprise | Model |
|---|---|---|---|
| CEXAI | Free (MIT OSS) | Implementation contract (scope-based) | OSS + services |
| LangChain | Free (OSS) | LangSmith $39/mo/user | Freemium SaaS |
| CrewAI | Free (OSS) | CrewAI Enterprise (undisclosed) | Freemium SaaS |
| AutoGen / DSPy | Free (OSS) | No tier | Pure OSS |
| LlamaIndex | Free (OSS) | LlamaCloud $39/mo/user | Freemium SaaS |

## Strategic Insights

**Top 3 Differentiators:**
1. Only typed artifact taxonomy + quality gates -- no competitor governs knowledge permanence
2. Self-assimilation: system improves itself from its own outputs (unique)
3. Implementation services with SLA -- enterprises get a delivery partner, not just a library

**2 Gaps to Acknowledge:**
1. Ecosystem: LangChain has 500k+ GitHub stars; CEXAI is newer (less community tooling)
2. RAG connectors: LlamaIndex has more pre-built loaders; CEXAI integrates but doesn't lead here

## Related Artifacts
| Artifact | Relationship | Score |
|---|---|---|
| kc_competitive_positioning | upstream | 0.80 |
| pitch_deck_intelligence_as_asset | sibling | 0.70 |
| p05_lp_cexai_oss_implementation_services | downstream | 0.65 |
