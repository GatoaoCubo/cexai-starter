---
id: p01_kc_model_context_protocol
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n01
title: "Model Context Protocol (MCP) -- Anthropic Standard for Tool Discovery"
version: 2.0.0
created: 2026-04-13
updated: 2026-05-02
quality: null
domain: research-intelligence
tags: [mcp, anthropic, tool-discovery, protocol, standard, agent-protocol]
tldr: "MCP is Anthropic's open standard (Nov 2024) for connecting LLMs to external tools, data, and prompts via JSON-RPC 2.0 servers. Adopted by OpenAI (Mar 2025), Google DeepMind (Apr 2025), Microsoft, and the Linux Foundation. CEX uses N07 as the sole MCP gateway with read-only enforcement."
when_to_use: "When evaluating tool-discovery protocols; when comparing CEX MCP support vs LangChain/CrewAI gaps; when designing N07 preflight architecture; when documenting cross-runtime tool access"
axioms:
  - "ALWAYS distinguish MCP (transport + discovery) from A2A (agent-to-agent coordination) -- they solve different layers"
  - "ALWAYS treat MCP as 'USB-C for LLM tools' (Anthropic's official analogy) -- one protocol, many providers"
  - "NEVER expose MCP credentials to non-orchestrator nuclei -- N07 is the sole gateway in CEX architecture"
  - "NEVER assume MCP-listed tools are safe -- enforce read-only by default; mutations require explicit permission"
keywords: [model context protocol, mcp, anthropic, json-rpc, tool discovery, mcp server, mcp client, protocol standard, agent interoperability]
density_score: 0.94
related:
  - p01_kc_competitor_langchain
  - p01_kc_competitor_crewai
  - p01_kc_competitive_intelligence_methods
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_preflight_mcp. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Model Context Protocol (MCP)

## Overview

Model Context Protocol (MCP) is an open standard introduced by Anthropic on November 25, 2024, for connecting Large Language Model applications to external systems (tools, data sources, prompts) through a unified JSON-RPC 2.0 transport. Anthropic's official analogy: "USB-C for AI applications" -- one protocol, many providers.

The protocol decouples LLM clients (Claude Desktop, Claude Code, Cursor, Cline) from tool servers (filesystem, GitHub, Postgres, browser, custom). Any client can talk to any server speaking MCP, eliminating the N x M integration matrix that plagued earlier agent ecosystems.

## Key Dates and Adoption

| Date | Event | Source |
|------|-------|--------|
| 2024-11-25 | Anthropic announces MCP (open spec + reference servers) | anthropic.com/news/model-context-protocol |
| 2024-12-15 | Reference servers released: filesystem, github, postgres, brave-search, slack | github.com/modelcontextprotocol/servers |
| 2025-03-26 | OpenAI announces MCP support across Agents SDK + ChatGPT desktop | openai.com (Sam Altman X post) |
| 2025-04-09 | Google DeepMind confirms Gemini SDK + infrastructure MCP support | deepmind.google |
| 2025-05 | Microsoft adopts MCP for Copilot Studio + Windows 11 | microsoft.com |
| 2025-09 | Linux Foundation forms MCP Working Group (governance neutrality) | linuxfoundation.org |
| 2026-04 | 1,000+ public MCP servers cataloged in mcp.so registry | mcp.so |

## Architecture (Three Components)

```
+--------------+      JSON-RPC 2.0       +-------------+
|   MCP Host   |  <------------------->  | MCP Server  |
|  (Claude     |   stdio | sse | http     | (filesystem,|
|   Desktop)   |                          |  github, db)|
+--------------+                          +-------------+
       |
       | embeds
       v
+--------------+
|  MCP Client  |
|  (per-server |
|   connection)|
+--------------+
```

| Component | Role | Examples |
|-----------|------|----------|
| Host | LLM application that consumes tools | Claude Desktop, Claude Code, Cursor, Cline, Continue |
| Client | Per-connection adapter inside the host | One client instance per active server |
| Server | Process exposing tools/resources/prompts | filesystem-server, github-server, postgres-server |

## Protocol Primitives

| Primitive | Purpose | Example |
|-----------|---------|---------|
| Tools | Callable functions (LLM-invoked) | `read_file(path)`, `query_database(sql)` |
| Resources | Read-only data sources (host-fetched) | file contents, DB rows, API responses |
| Prompts | Pre-defined prompt templates | `summarize_pr`, `review_diff` |
| Sampling | Server requests LLM completion from host | rare; used for nested reasoning |
| Roots | Workspace directories the server may access | `file:///workspace/repo` |

## Transport Layers

| Transport | When to use | Latency | Auth |
|-----------|-------------|---------|------|
| stdio | Local process (filesystem, git, docker) | <5ms | OS process boundary |
| SSE (Server-Sent Events) | Remote HTTP server (web tools) | 50-200ms | OAuth / API key in header |
| HTTP+streaming | Modern remote, post-2025 spec | 50-150ms | OAuth 2.1 + PKCE |

## CEX Implementation

CEX treats MCP as a Phase 0 preflight gather rather than runtime exposure:

| Layer | File | Behavior |
|-------|------|----------|
| Gateway | `_tools/cex_preflight_mcp.py` | N07 only -- gathers external context BEFORE dispatch |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
| Permissions | `.claude/nucleus-settings/n07.json` | GitHub MCP read-only; mutations denied |
| Provider config | `.cex/config/preflight_sources.yaml` | Free defaults (fetch, github) + opt-in premium (firecrawl) |
| Audit trail | `.cex/cache/preflight/{hash}_audit.json` | Every preflight gather logged with token cost |
| Security policy | `_docs/specs/spec_mcp_security_policy.md` | Defense-in-depth + secret hygiene |

This architecture means non-Claude runtimes (Codex, Gemini, Ollama) never need MCP credentials -- they receive pre-compiled context inline through the External Context section in handoffs. Live-MCP kinds (browser_tool, mcp_server, computer_use) hard-route to Claude.

## Competitive Landscape (April 2026)

| Framework | Native MCP | A2A | Notes |
|-----------|-----------|-----|-------|
| Anthropic Claude (Desktop, Code, Cursor) | YES (origin) | partial | Reference implementation |
| OpenAI Agents SDK | YES (Mar 2025) | partial | First-class MCP client |
| Google DeepMind Gemini SDK | YES (Apr 2025) | partial | Adopted via working group |
| Microsoft Copilot Studio | YES (May 2025) | partial | Windows 11 integration |
| LangChain / LangGraph | NO (custom wrapper required) | NO | OpenAgents.org Feb 2026 audit confirmed gap |
| CrewAI 1.0+ | YES (Oct 2025) | NO | Consumption-only via MCP Registry |
| AutoGen 0.4+ | partial | NO | Tool-discovery only, no resources/prompts |
| LlamaIndex | partial (via plugin) | NO | Not first-class |
| CEX | YES (N07 gateway, Phase 0 preflight) | YES (the Task tool + handoffs) | Read-only enforced |

## Strategic Significance

1. **Standard convergence**: Anthropic + OpenAI + Google + Microsoft + Linux Foundation alignment is rare. MCP has the strongest convergence signal of any agent protocol.
2. **Decouples runtime from tools**: LangChain's tightly-coupled ecosystem is a liability vs MCP's vendor-neutrality.
3. **Audit primitive**: Every MCP call is logged at the host layer -- enterprise compliance friendly.
4. **CEX positioning advantage**: N07-as-gateway pattern (single MCP credential surface, read-only by default) is unique vs frameworks that expose MCP per-agent.

## Anti-Patterns

| Anti-Pattern | Why It Fails | CEX Mitigation |
|-------------|--------------|----------------|
| Per-agent MCP credentials | Credential sprawl; mutation risk per agent | N07 sole gateway |
| Trusting tool output blindly | Servers can return prompt injection | Read-only default + audit log |
| Treating MCP as A2A replacement | MCP = tool discovery, not agent coordination | Use the Task tool for A2A |
| No transport pinning | stdio vs SSE auth surfaces differ | Pin per-server in preflight_sources.yaml |

## Sources

- Anthropic MCP announcement (Nov 25, 2024): https://www.anthropic.com/news/model-context-protocol
- MCP specification: https://spec.modelcontextprotocol.io/
- Reference servers: https://github.com/modelcontextprotocol/servers
- OpenAI MCP support (Mar 26, 2025): https://openai.com/index/new-tools-for-building-agents/
- Google DeepMind MCP confirmation (Apr 2025): https://deepmind.google/
- Linux Foundation MCP Working Group (Sep 2025): https://www.linuxfoundation.org/
- mcp.so registry (1,000+ servers, Apr 2026): https://mcp.so/
- OpenAgents.org agent framework comparison (Feb 23, 2026): https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_competitor_langchain]] | sibling | 0.42 |
| [[p01_kc_competitor_crewai]] | sibling | 0.40 |
| atom_02_mcp_protocol | sibling | 0.38 |
| [[p01_kc_competitive_intelligence_methods]] | upstream | 0.30 |
| n07-orchestrator | downstream | 0.28 |
