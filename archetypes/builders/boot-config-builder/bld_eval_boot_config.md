---
kind: quality_gate
id: p11_qg_boot_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of boot_config artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: boot_config"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "boot-config"
  - "P11"
  - "P02"
  - "governance"
  - "initialization"
  - "provider"
tldr: "Gates for boot_config artifacts — provider-specific agent initialization parameters and constraints."
domain: boot_config
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords:
  - "gates for boot_config artifacts"
  - "quality-gate"
  - "boot-config"
  - "governance"
  - "initialization"
  - "provider"
  - "^p02_boot_[a-z][a-z0-9_]+$"
density_score: 0.88
related:
  - boot-config-builder
---
## Quality Gate

# Gate: boot_config
## Definition
| Field     | Value                                                  |
|-----------|--------------------------------------------------------|
| metric    | provider completeness + constraint rationalization     |
| threshold | 8.0                                                    |
| operator  | >=                                                     |
| scope     | all boot_config artifacts (P02)                        |
## HARD Gates
All must pass. Failure on any = final score 0.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = agent fails to boot |
| H02 | id matches `^p02_boot_[a-z][a-z0-9_]+$` | Namespace compliance |
| H03 | id == filename stem | Discovery relies on this |
| H04 | kind == "boot_config" | Type integrity |
| H05 | quality == null | Never self-score |
| H06 | All 15 required fields present: id, kind, pillar, version, created, updated, author, provider, identity, constraints, tools, domain, quality, tags, tldr | Completeness |
| H07 | identity object has name, role, agent_group | Identity block completeness |
| H08 | constraints object has max_tokens, context_window, timeout_seconds | Runtime constraints completeness |
| H09 | tools is non-empty list | Agent requires at least one tool to function |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty, not filler | 1.0 |
| S02 | tags is list, len >= 3, includes "boot-config" | 0.5 |
| S03 | model field is set to specific model identifier | 0.5 |
| S04 | temperature is float 0.0-2.0 | 0.5 |
| S05 | flags list present and non-empty | 0.5 |
| S06 | mcp_config present when provider supports MCP | 1.0 |
| S07 | body has ## Constraints table with per-field rationale | 1.0 |
| S08 | body has ## Tools Configuration table listing each tool | 1.0 |
| S09 | density_score >= 0.80 | 0.5 |
| S10 | No filler phrases or generic descriptions | 1.0 |
Weights sum: 7.5. Normalize: divide each by 7.5 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as reference config for this provider |
| >= 8.0 | PUBLISH — active boot configuration |
| >= 7.0 | REVIEW — rationalize constraints or complete tools list |
| < 7.0  | REJECT — identity block or constraints block incomplete |
## Bypass
| Field | Value |
|-------|-------|
| conditions | New provider integration requiring immediate bootstrap before full spec |
| approver | p02-chief |
| audit_trail | Log in records/audits/ with provider justification and timestamp |
| expiry | 48h — complete constraints spec required before expiry |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples: boot-config-builder
## Golden Example
INPUT: "Create boot config for a research agent on Claude Code provider"
OUTPUT:
```yaml
id: p02_boot_claude_code_research
kind: boot_config
pillar: P02
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
provider: "claude_code"
identity:
  name: "Research Agent"
  role: "Deep web research and knowledge extraction"
  agent_group: "agnostic"
constraints:
  max_tokens: 16384
  context_window: 200000
  timeout_seconds: 300
  max_retries: 2
  temperature: 0.3
tools: [brain_query, web_search, web_fetch, read, grep, glob]
model: "claude-sonnet-4-6"
temperature: 0.3
flags: [--no-chrome, --strict-mcp-config]
mcp_config:
  brain: stdio
  firecrawl: stdio
permissions:
  read: [records/, archetypes/]
  write: [records/pool/]
  execute: [python, git]
system_prompt_ref: "p03_sp_research_agent"
domain: "research"
quality: 8.9
tags: [boot-config, research, claude-code, P02]
tldr: "Claude Code boot config for research agent with brain+firecrawl MCPs and 200K context"
density_score: 0.89
```
## Provider Overview
Claude Code CLI runtime for research-focused agents.
Supports MCP servers, 200K context window, file system access.
## Identity Block
Name: Research Agent
Role: Deep web research and knowledge extraction
Agent_group: agnostic (cross-agent_group utility)
## Constraints
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| max_tokens | 16384 | Research outputs need extended generation |
| context_window | 200000 | Claude Sonnet 4.6 full context |
| timeout_seconds | 300 | Web research may take 3-5 minutes |
| max_retries | 2 | Retry transient web fetch failures |
## Tools Configuration
| Tool | Type | Purpose |
|------|------|---------|
| brain_query | mcp | Search existing knowledge in pool |
| web_search | mcp | Discover relevant URLs |
| web_fetch | mcp | Extract content from URLs |
| read | cli | Read local files |
| grep | cli | Search file contents |
| glob | cli | Find files by pattern |
## Flags
| Flag | Purpose |
|------|---------|
| --no-chrome | No browser needed for CLI research |
| --strict-mcp-config | Only use declared MCP servers |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
