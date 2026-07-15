---
kind: quality_gate
id: p11_qg_handoff_protocol
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of handoff_protocol artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: handoff_protocol"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "handoff-protocol"
  - "P02"
tldr: "Pass/fail gate for handoff_protocol artifacts: required fields, id pattern, body sections, parameter completeness."
domain: "agent-to-agent handoff and context transfer"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords:
  - "required fields"
  - "id pattern"
  - "body sections"
  - "parameter completeness"
  - "quality-gate"
  - "handoff-protocol"
  - "kind: handoff_protocol"
density_score: 0.90
related:
  - handoff-protocol-builder
  - p11_qg_memory_scope
  - bld_instruction_handoff_protocol
  - p11_qg_chunk_strategy
  - p11_qg_retriever_config
---
## Quality Gate

# Gate: handoff_protocol
## Definition
| Field | Value |
|---|---|
| metric | handoff_protocol artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: handoff_protocol` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p02_handoff_[a-z][a-z0-9_]+$` | ID contains uppercase, spaces, or invalid chars |
| H03 | ID equals filename stem | id field != filename without extension |
| H04 | Kind equals literal `handoff_protocol` | Any other kind value |
| H05 | Quality field is null | Any non-null value |
| H06 | All required fields present | Missing quality, tags, tldr or other required fields |
| H07 | All required body sections present | Missing ## Overview or ## Trigger or ## Context Transfer or ## Return Contract |
| H08 | Body <= 2048 bytes | Body exceeds size limit |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Parameter completeness | 1.0 | All parameters have concrete values (no placeholders) |
| Rationale quality | 1.0 | Each parameter value has clear rationale |
| Pattern selection | 1.0 | Correct pattern chosen for the use case |
| Boundary clarity | 1.0 | Explicitly states what this IS and IS NOT |
| Integration mapping | 0.5 | Upstream and downstream connections documented |
| Density | 1.0 | Information density >= 0.8, no filler content |
| Tags quality | 0.5 | Tags >= 3, includes "handoff_protocol", relevant to content |
| Tldr quality | 0.5 | Tldr <= 160 chars, dense, accurate summary |
| Domain specificity | 1.0 | Parameters and values specific to declared domain |
| Testability | 0.5 | Configuration can be validated with known inputs |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |

## Examples

# Examples: handoff-protocol-builder
## Golden Example
INPUT: "Create handoff protocol for research delegation from orchestrator to research_agent"
OUTPUT:
```yaml
id: p02_handoff_stella_to_shaka
kind: handoff_protocol
pillar: P02
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "orchestrator-to-research_agent Research Delegation"
quality: null
tags: [handoff_protocol, P02, handoff]
tldr: "orchestrator-to-research_agent Research Delegation — production-ready handoff_protocol configuration"
```
## Overview
Handoff protocol for delegating research tasks from orchestrator (orchestrator) to research_agent (research agent_group).
orchestrator detects research intent, composes context, and dispatches via handoff file.

## Trigger
Condition: task keywords match [research, analyze, investigate, compare, benchmark, scrape].
Confidence threshold: >= 0.7 keyword match score.
Pre-check: verify research_agent is not already running (signal file check).

## Context Transfer
| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| query | string | YES | Research question in natural language |
| domain | string | YES | Knowledge domain (e-commerce, tech, market) |
| depth | enum: shallow, medium, deep | YES | Research thoroughness level |
| deadline | datetime | NO | When results are needed |
| output_format | enum: kc, report, bullets | YES | Shape of deliverable |
| seeds | list[string] | NO | Seed keywords to guide research |

## Return Contract
```yaml
findings: list[string]    # Key findings, min 3 items
sources: list[url]        # Verified source URLs
confidence: float         # 0.0-1.0 research confidence
summary: string           # 2-3 sentence executive summary
signal_file: path         # Path to completion signal
```
Timeout: 30 minutes. Retry: 1x with simplified query. Escalation: return partial results.
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p02_handoff_ pattern (H02 pass)
- kind: handoff_protocol (H04 pass)
- All required fields present (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
