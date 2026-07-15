---
kind: quality_gate
id: p11_qg_agent
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of agent artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: agent"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "agent"
  - "P11"
  - "P02"
  - "governance"
  - "identity"
  - "agent-package"
tldr: "Gates for agent artifacts — persona + capabilities + agent_package packages ready for deploy."
domain: agent
created: "2026-03-27"
updated: "2026-03-27"
last_reviewed: "2026-04-18"
8f: "F7_govern"
keywords:
  - "gates for agent artifacts"
  - "quality-gate"
  - "agent"
  - "governance"
  - "identity"
  - "agent-package"
  - "^p02_agent_[a-z][a-z0-9_]+$"
density_score: 0.90
related:
  - agent-builder
  - bld_collaboration_agent
  - bld_instruction_agent
  - bld_architecture_agent
  - bld_knowledge_card_agent
---
## Quality Gate

# Gate: agent
## Definition
| Field     | Value                                               |
|-----------|-----------------------------------------------------|
| metric    | identity completeness + agent_package navigability |
| threshold | 8.0                                                 |
| operator  | >=                                                  |
| scope     | all agent artifacts (P02)                           |
## HARD Gates
All must pass. Failure on any = final score 0.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = broken agent boot |
| H02 | id matches `^p02_agent_[a-z][a-z0-9_]+$` | Namespace compliance |
| H03 | id == filename stem | Brain search relies on this |
| H04 | kind == "agent" | Type integrity |
| H05 | quality == null | Never self-score |
| H06 | All 10 required fields present: id, kind, pillar, title, version, agent_group, domain, quality, tags, tldr | Completeness |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty, not filler | 1.0 |
| S02 | tags is list, len >= 3, includes "agent" | 0.5 |
| S03 | agent_package section lists >= 10 spec files | 1.0 |
| S04 | routing_keywords is list, len >= 4 | 0.5 |
| S05 | body has ## File Structure with correct spec naming convention | 1.0 |
| S06 | capabilities_count matches actual bullets in Architecture section | 1.0 |
Weights sum: 7.5. Normalize: divide each by 7.5 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as reference agent definition |
| >= 8.0 | PUBLISH — register in routing index, deploy agent_package |
| >= 7.0 | REVIEW — complete agent_package or sharpen domain boundary |
| < 7.0  | REJECT — rework identity and capability scope |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Critical agent_group gap requiring immediate agent deploy |
| approver | p02-chief |
| audit_trail | Log in records/audits/ with justification and timestamp |
| expiry | 72h — full gate pass required before expiry |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples: agent-builder
## Golden Example
INPUT: "Create agent definition for a knowledge-card-builder agent"
OUTPUT:
```yaml
id: p02_agent_knowledge_card_builder
kind: agent
pillar: P02
title: "Knowledge Card Builder Agent"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
```
## Overview
knowledge-card-builder is a knowledge-engine specialist in knowledge distillation.
Converts raw sources into atomic searchable knowledge_card artifacts with density >= 0.80.
## Architecture
Capabilities: distill raw text to atomic facts, score density, produce P01 frontmatter,
validate sources, detect boundary (knowledge_card vs context_doc vs glossary_entry).
Tools: brain_query [MCP] (dedup check), validate_artifact.py [PLANNED].
Agent_group: knowledge-engine | Upstream: researcher | Downstream: knowledge-index-builder.
## File Structure
```
agents/knowledge_card_builder/agent_package/
  ISO_KNOWLEDGE_CARD_BUILDER_001_MANIFEST.md
  ISO_KNOWLEDGE_CARD_BUILDER_002_QUICK_START.md
  ISO_KNOWLEDGE_CARD_BUILDER_003_PRIME.md
  ISO_KNOWLEDGE_CARD_BUILDER_004_INSTRUCTIONS.md
  ISO_KNOWLEDGE_CARD_BUILDER_005_ARCHITECTURE.md
  ISO_KNOWLEDGE_CARD_BUILDER_006_OUTPUT_TEMPLATE.md
  ISO_KNOWLEDGE_CARD_BUILDER_007_EXAMPLES.md
```
## When to Use
Triggers: "create knowledge card for X", "distill research into atomic facts"
NOT when: full narrative needed (context_doc), term definition only (glossary_entry)
## Input / Output
Input: raw_source (text/URL/file), domain. Output: p01_kc_{slug}.md + density report.
Receives from: researcher. Produces for: knowledge_index, pool (quality >= 8.0).
## Common Issues
1. Generic bullets: compress to concrete data, remove filler
2. Missing source: verify before citing
3. Boundary: narrative -> context-doc-builder
WHY THIS IS GOLDEN:
- quality: null (H05 pass) | id p02_agent_ pattern (H02 pass) | kind: agent (H04 pass)
- 19 fields (H06 pass) | llm_function: BECOME (H07 pass) | agent_group: knowledge-engine (H08 pass)
- agent_package 10 files (S05 pass) | capabilities_count: 5 matches body (S06 pass)
- tldr: 71ch (S01 pass) | density: 0.87 (S09 pass) | no filler (S10 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
