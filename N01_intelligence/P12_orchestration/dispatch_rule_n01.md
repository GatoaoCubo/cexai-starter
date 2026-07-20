---
id: dispatch_rule_n01
kind: dispatch_rule
pillar: P12
title: "Dispatch Rule: N01 Research & Intelligence"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: "n01_intelligence"
quality: null
tags: [dispatch, routing, orchestration, n01, research]
tldr: "Routes complex research, analysis, and synthesis tasks to the N01 Research & Intelligence Nucleus based on semantic intent, keywords, and trigger phrases."
target_agent: "n01_agent_intelligence"
priority: 10
confidence_threshold: 0.85
fallback_agent: "n04_knowledge"
keywords: [trigger phrase match, semantic intent analysis, keyword match, rag, literature review, competitor analysis, benchmark, synthesis, trend report]
density_score: 0.95
related:
  - p12_sc_research_n01
  - p12_wf_intelligence
  - p12_ct_research_sprint
  - nucleus_def_n01
  - p06_is_n01
---

## 1. PURPOSE
This rule identifies and routes tasks that require deep, analytical research and synthesis to the **N01 Research & Intelligence Nucleus**. The goal is to ensure that complex, long-running analytical jobs are handled by the appropriate specialist agent instead of a generalist agent.

## 2. ROUTING STRATEGY: HIERARCHICAL
Routing is determined by a hierarchical evaluation:
1.  **Trigger Phrase Match**: Highest weight. Direct match to common N01 tasks.
2.  **Semantic Intent Analysis**: The core of the strategy. The system evaluates if the user's underlying goal is research and synthesis.
3.  **Keyword Match**: Lowest weight. Used as a supporting signal.

## 3. TRIGGER PHRASES (HIGH CONFIDENCE)
If the prompt starts with or contains these phrases, route to N01 with high confidence:
- "Research the state of..."
- "Analyze the competitive landscape of..."
- "Provide a literature review on..."
- "Summarize the key findings from these papers..."
- "Benchmark X against Y on..."
- "Create a trend report for..."
- "Conduct a competitor analysis of..."

## 4. CORE KEYWORDS (MEDIUM CONFIDENCE)
Presence of these keywords strongly suggests N01 is the correct agent:
- `research`
- `analysis`
- `competitor`
- `intelligence`
- `papers`
- `trends`
- `summarize` (in the context of long documents)
- `benchmark`
- `RAG`
- `literature review`
- `market analysis`
- `synthesis`
- `findings`

## 5. EXCLUSION CRITERIA (ANTI-PATTERNS)
Even if keywords match, **DO NOT** route to N01:

| Query Type | Example | Route Instead |
|------------|---------|---------------|
| Simple factual questions | "What is React?" | N04 Knowledge |
| Code writing requests | "Write a Python script for data parsing" | N05 Operations |
| Creative content | "Write a poem about AI" | N02 Marketing |
| Operational actions | "Restart the server", "Deploy to prod" | N05 Operations |
| Real-time info | "What's the weather?", "Latest stock price" | External API |
| Quick definitions | "Define machine learning" | N04 Knowledge |
| Build requests | "Create a new component", "Generate docs" | N03 Builder |
| Single-source summary | "Summarize this one article" | N04 Knowledge |
| Implementation tasks | "How do I configure X?" | N05 Operations |

## 6. FALLBACK LOGIC
If the routing confidence score is below the `confidence_threshold` (0.85), or if the N01 agent is offline or at capacity, the task MUST be routed to the `n04_knowledge` nucleus. N04 serves as the general-purpose knowledge agent and can handle broader, less specialized queries, ensuring system resilience.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_sc_research_n01]] | sibling | 0.35 |
| [[p12_wf_intelligence]] | sibling | 0.33 |
| [[p12_ct_research_sprint]] | related | 0.31 |
| [[nucleus_def_n01]] | upstream | 0.28 |
| [[p06_is_n01]] | downstream | 0.26 |
