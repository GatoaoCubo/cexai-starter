---
id: p01_kc_competitive_agent_frameworks
kind: knowledge_card
pillar: P01
nucleus: n01
domain: competitive-intelligence
version: 1.0.0
created: 2026-05-05
quality: null
tags: [competitor, synthesis, langchain, autogpt, crewai, autogen, dspy, llamaindex]
when_to_use: "Positioning CEXAI against the 6 dominant agent frameworks; designing CEXAI features by adoption (proven primitive) or differentiation (exploitable gap)"
axioms:
  - "ALWAYS frame each competitor as (pattern to adopt, gap to exploit)"
  - "ALWAYS treat 8F + 12 pillars + 125 kinds as the structural moat none of the 6 have"
  - "NEVER claim parity on stars / downloads -- compete on typed-knowledge governance"
  - "NEVER ignore AutoGen lifecycle lesson: corporate-owned OSS deprecates fast"
tldr: "Six dominant agent frameworks -- LangChain (124K), AutoGPT (184K), CrewAI (49.8K), AutoGen (57K, EOL), DSPy (Stanford), LlamaIndex (48.9K) -- each ship one primitive worth adopting and leave one structural gap CEXAI exploits via typed knowledge + 8F + multi-runtime sovereignty."
8f: "F3_inject"
keywords: [competitive synthesis, pattern adoption, exploitable gap, typed knowledge, multi-runtime, 8f, mcp gateway]
related:
  - p01_kc_competitor_langchain
  - p01_kc_competitor_crewai
  - p01_kc_competitor_autogen
  - p01_kc_competitor_llamaindex
  - p01_kc_competitive_intelligence_methods
  - cm_cex_vs_landscape
---

# Competitive Synthesis: 6 Agent Frameworks vs CEXAI

> N01 Analytical Envy lens. Each framework = 1 pattern to adopt + 1 gap to exploit.

## Snapshot Matrix (April 2026)

| Framework | Stars | MCP | Pivot | Detailed KC |
|-----------|------:|-----|-------|-------------|
| AutoGPT | 184K | yes (blocks) | Visual block builder + marketplace | (this KC) |
| LangChain / LangGraph | 124K + 30K | none native | Graph runtime + LangSmith SaaS | [[p01_kc_competitor_langchain]] |
| AutoGen | 57K | retrofit | EOL Oct 2025 -> MS Agent Framework | [[p01_kc_competitor_autogen]] |
| CrewAI | 49.8K | native (1.0+) | Role-crew + Flows + Cloud | [[p01_kc_competitor_crewai]] |
| LlamaIndex | 48.9K | native (bidi) | Document Agent Platform | [[p01_kc_competitor_llamaindex]] |
| DSPy | ~22K | none native | Programming not prompting; optimizers | -- |

## Per-framework: Pattern + Gap

### LangChain / LangGraph
- **Adopt:** the **Hub + Templates flywheel** -- 1M+ shared chains in langchain hub. Mirror: a public registry of N00 archetypes + crew_templates so contributed cells become discoverable across CEXAI instances.
- **Exploit:** **no native MCP / A2A** (OpenAgents.org Feb 2026). LangChain still requires custom glue. CEXAI N07 is MCP-native (Phase 0 preflight); the Task tool + handoffs are A2A by construction.

### AutoGPT (Significant-Gravitas)
- **Adopt:** **composable blocks with explicit IO + transformations** + visual workflow builder + agent marketplace. CEXAI's 12 builder ISOs already mimic block typing -- the gap is the visual layer + marketplace surface.
- **Exploit:** **no governance layer, no quality gate**. Blocks are typed at the IO boundary but outputs unscored. CEXAI enforces F7 GOVERN with 9.0 target on every artifact.

### CrewAI
- **Adopt:** **role + goal + backstory in plain English** as the agent spec primitive (faster time-to-first-crew than any graph framework). CEXAI WAVE8 already has role_assignment; tighten the natural-language slot to CrewAI ergonomics.
- **Exploit:** **no typed-knowledge taxonomy + Python-only**. Session-scoped memory. CEXAI runs Claude/Codex/Gemini/Ollama and persists into 125 kinds across 12 pillars.

### AutoGen (Microsoft Research)
- **Adopt:** **conversation log as inspectable trace** + sandboxed code execution. Borrow the trace primitive into trace_config + reasoning_trace kinds.
- **Exploit:** **lifecycle collapse risk in corporate OSS** + non-deterministic routing. AutoGen entered maintenance Oct 2025; users migrating to MS Agent Framework. CEXAI is community + sovereign; routing is deterministic.

### DSPy (Stanford NLP)
- **Adopt:** **Signatures + Optimizers (MIPROv2, COPRO)** -- declarative IO contracts auto-tuned against a metric, not hand-prompted. CEXAI already ships prompt_optimizer + prompt_compiler kinds; wire them into a DSPy-style compile loop so artifacts auto-improve against eval_dataset metrics.
- **Exploit:** **no orchestration, no nuclei, no multi-artifact taxonomy**. DSPy optimizes individual programs; CEXAI orchestrates 8 nuclei x 12 pillars across whole missions. DSPy is a primitive; CEXAI is the operating system.

### LlamaIndex
- **Adopt:** **Workflows-as-MCP-server bidirectional pattern** (consume MCP tools AND expose flows as MCP servers). Mirror: expose every crew_template + chain as an MCP endpoint so external agents can call CEXAI as a service.
- **Exploit:** **indexing without typed governance**. LlamaIndex retrieves whatever you ingest; no quality scoring, no pillar boundaries, no peer review. CEXAI types every knowledge_card and runs F7 GOVERN before commit.

## Cross-cutting Synthesis

| Top 3 Patterns to Adopt | Top 3 Gaps to Exploit |
|-------------------------|------------------------|
| 1. Hub/marketplace surface (LangChain + AutoGPT) | 1. No typed-artifact governance anywhere |
| 2. Plain-English role spec (CrewAI) | 2. Single-runtime lock-in everywhere except CEXAI |
| 3. Optimizer-driven prompt compile (DSPy) | 3. MCP/A2A absent (LangChain, DSPy) or retrofit (AutoGen) |

## Sources

- AutoGPT 184K + visual blocks + MCP: [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) ; [PyShine 2026-04](https://pyshine.com/2026/04/20/autogpt-platform-continuous-ai-agents/)
- DSPy Signatures / Modules / Optimizers: [dspy.ai](https://dspy.ai/) ; [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) ; [arXiv 2310.03714](https://arxiv.org/pdf/2310.03714)
- LangChain Series B + ecosystem: [[p01_kc_competitor_langchain]] (12 sources)
- CrewAI 1.0 GA + 60% F500: [[p01_kc_competitor_crewai]]
- AutoGen EOL Oct 2025: [[p01_kc_competitor_autogen]]
- LlamaIndex bidi MCP + DAP pivot: [[p01_kc_competitor_llamaindex]]
- Cross-framework: [OpenAgents.org 2026-02-23](https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared)
