---
kind: quality_gate
id: p11_qg_agent-card
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of agent_card artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Agent_group Spec'
version: 1.0.0
author: builder_agent
tags:
- eval
- P11
- quality_gate
- examples
tldr: Gates ensuring agent_group spec files define a fully autonomous agent with role,
  model, tools, boot sequence, and dispatch rules.
domain: agent_card
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords: [agent_group spec, agent_card, quality gate, scoring dimensions]
density_score: 0.97
related:
  - agent-card-builder
---
## Quality Gate

## Definition
A agent_group spec describes a fully autonomous agent: its identity, the LLM it runs on, the external tools it can call, how it starts up, how it receives work, and how it shuts down. A spec passes this gate when any operator could launch and operate the agent_group from the document alone, without consulting the author.
## HARD Gates
Failure on any HARD gate = immediate REJECT regardless of score.
| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML with no syntax errors | Unparseable file cannot be indexed or validated |
| H02 | `id` matches the file's directory namespace (`agent-card-builder/...`) | Mismatched IDs cause routing failures |
| H03 | `id` value equals the filename stem (slug portion) | Filename and ID must be the same addressable key |
| H04 | `kind` is exactly `agent_card` (literal match, no variation) | Kind drives the loader; wrong literal silently misroutes |
| H05 | `quality` field is `null` (not filled by author) | Quality is assigned by this gate, not self-reported |
| H06 | All required frontmatter fields present: id, kind, pillar, title, version, created, updated, author, domain, tags, tldr | Incomplete frontmatter breaks downstream consumers |
## SOFT Scoring
Dimensions are weighted; total normalized weight = 100%.
| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | density >= 0.80 (content per token ratio) | 1.0 | Padded with filler prose | Mostly substantive | No filler; every sentence carries information |
| 2 | Constraints documented (what the agent_group must never do) | 1.0 | No constraints listed | Partial list, vague | Explicit NEVER list with rationale per constraint |
| 3 | Dispatch rules present (how the agent_group receives and accepts tasks) | 1.0 | No dispatch described | Dispatch channel named, no detail | Full dispatch protocol: channel, format, acceptance criteria |
| 4 | Scaling rules defined (concurrency limits, queue behavior, overflow handling) | 0.5 | No mention | Single-instance only documented | Concurrency limits, queue behavior, and overflow all defined |
| 5 | Monitoring configuration (signals emitted, health check, alerting thresholds) | 1.0 | No monitoring | Logs only | Structured signals + health check + alerting thresholds |
| 6 | Tags include `agent-card` | 0.5 | Missing | Present but misspelled | Exactly `agent-card` in tags list |

## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish as exemplar |
| >= 8.0 | PUBLISH | Ready for runtime |
| >= 7.0 | REVIEW | Flag for review |
| < 7.0  | REJECT | Rework required |

## Bypass
| Field | Value |
|-------|-------|
| conditions | Experimental agent_card artifact under active A/B testing |
| approver | Nucleus lead (written approval required) |
| audit_trail | Log in records/audits/ with bypass reason and timestamp |
| expiry | 48h — must pass all gates before expiry |
| never_bypass | H01 (YAML parse), H05 (quality null) |

## Examples

# Examples: agent-card-builder
## Golden Example
INPUT: "Especifica o agent_group researcher for research de mercado"
OUTPUT:
```yaml
id: p08_ac_shaka
kind: agent_card
pillar: P08
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
name: "researcher"
```
## Role
Research agent_group focused on market intelligence, competitor analysis, and web data extraction.
Primary function: gather, structure, and deliver research findings as knowledge cards or reports.
Does not generate code or modify production systems.
## Model & MCPs
- **Model**: sonnet (balanced cost/quality for research tasks)
- **firecrawl**: web scraping and structured data extraction (3000 credits/month)
- **brain**: knowledge search and deduplication check
## Boot Sequence
1. Load prime_researcher.md (identity, constraints, dispatch protocol)
2. Initialize firecrawl MCP (verify API key, check credit balance)
3. Initialize brain MCP (verify Ollama running, index freshness)
4. Check dispatch queue (.claude/handoffs/shaka_*.md)
## Dispatch
Keywords: researchr, market, competitor, scrape, analysis, research
Routing: orchestrator matches keywords against dispatch_keywords list.
Priority: research tasks routed to researcher before any other agent_group.
## Constraints
- Read-only: never modify production data or commit to main
- Budget: max 10 firecrawl credits per research session
- Boundary: no code generation (delegate to builder)
- Quality: all findings must include source URLs
## Dependencies
- brain MCP server (Ollama + FAISS index)
- firecrawl API ($19/month tier)
- No sibling agent_group dependencies (fully independent)
## Scaling & Monitoring
- Max 1 concurrent instance (avoid firecrawl rate limits)
- 30-minute timeout per session
- Signal on complete: emits p12_sig_shaka_complete.json
- Alert on failure: logs error + notifies orchestrator
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p08_ac_ pattern (H02 pass)
- kind: agent_card (H04 pass)
- 26 frontmatter fields present (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` populated (3-15 entries), 1+ upstream, 1+ downstream
- Penalty: -0.3 if empty

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p11_qg_dispatch_rule | sibling | 0.36 |
| [[agent-card-builder]] | upstream | 0.34 |
| [[bld_orchestration_agent_card]] | upstream | 0.33 |
| p11_qg_quality_gate | sibling | 0.33 |
