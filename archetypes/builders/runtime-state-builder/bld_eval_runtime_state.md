---
kind: quality_gate
id: p11_qg_runtime_state
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of runtime_state artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Runtime State'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: 'Quality gate for agent runtime mental state: verifies routing rules, state
  transitions, persistence scope, and conflict resolution.'
domain: runtime_state
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords: [runtime state, verifies routing rules, kind: runtime_state, yaml.safe_load(frontmatter), p10_rs_*, id.startswith("p10_rs_"), path(file).stem == id]
density_score: 0.85
related:
  - runtime-state-builder
---
## Quality Gate

## Definition
A runtime state artifact captures the live decision-making configuration of an agent: its routing rules (with conditions and confidence), state transitions (with trigger events), priority ordering, and heuristics. It applies only during execution — it contains no design-time content such as capability descriptions or architectural diagrams. Persistence scope declares whether state survives across sessions or resets each time.
Scope: files with `kind: runtime_state`. Does not apply to mental models (design-time identity), system prompts (static instructions), or session state (ephemeral task context).
## HARD Gates
Failure on any single gate means REJECT regardless of soft score.
| ID  | Predicate | How to test |
|-----|-----------|-------------|
| H01 | Frontmatter parses as valid YAML | `yaml.safe_load(frontmatter)` raises no error |
| H02 | `id` matches namespace `p10_rs_*` | `id.startswith("p10_rs_")` is true |
| H03 | `id` equals filename stem | `Path(file).stem == id` |
| H04 | `kind` equals literal `runtime_state` | string equality check |
| H05 | `quality` is null at authoring time | `quality is None` |
| H06 | All required frontmatter fields present and non-empty | id, kind, pillar, title, version, created, updated, author, domain, tags, tldr, agent, persistence all present |
## SOFT Scoring
Score each dimension 0 (absent or fails) to 1 (present and passes). Weights are 0.5 or 1.0.
| #  | Dimension | Weight |
|----|-----------|--------|
| 1  | `density_score` field present and >= 0.80 | 1.0 |
| 2  | Every routing rule has an explicit condition (not a vague keyword) | 1.0 |
| 3  | Every state transition has a named trigger event (not just a description) | 1.0 |
| 4  | Priority ordering present with rationale for each rank | 1.0 |
| 5  | Heuristics section present with at least 2 rules of thumb and their confidence levels | 1.0 |
| 6  | Domain map present with explicit boundary (what this agent handles vs. what it defers) | 1.0 |
**Formula**: `final_score = (sum of score_i * weight_i) / (sum of weight_i) * 10`
Weight total: 10.0. Each dimension contributes proportionally. Score range: 0.0 to 10.0.
## Actions
| Tier | Threshold | Action |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publish to pool as golden; use as reference for agent state design |
| PUBLISH | >= 8.0 | Publish to pool; mark production-ready |
| REVIEW | >= 7.0 | Return to author with scored dimension feedback; one revision cycle allowed |
| REJECT | < 7.0 | Block from pool; full rewrite required before re-evaluation |
## Bypass
| Field | Value |
|-------|-------|
| condition | Agent is in early bootstrapping and fewer than 2 routing rules have been observed in forctice |
| approver | Domain lead must approve in writing before bypass takes effect |

## Examples

# Examples: runtime-state-builder
## Golden Example
INPUT: "Create runtime_state for the research agent (researcher) defining routing and priorities at runtime"
OUTPUT:
```yaml
id: p10_rs_researcher
kind: runtime_state
pillar: P10
title: "Runtime State: Researcher Agent"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
```text
incoming_query
  ├── is_structured_data? -> API-direct route
  ├── pool_match >= 0.85? -> Pool-first route
  ├── pool_match >= 0.60? -> Web-fallback route
  └── complex_query? -> Multi-source route
```
## Priorities
1. Accuracy — prefer verified sources over speed
2. Freshness — prefer recent data over cached (max 7d stale)
3. Cost efficiency — minimize API calls when pool suffices
4. Completeness — cover all facets of multi-part queries
## Heuristics
| Heuristic | When | Confidence |
|-----------|------|------------|
```
WHY THIS IS GOLDEN:
- quality: null (H06 pass)
- id matches p10_rs_ pattern (H02 pass)
- kind: runtime_state (H04 pass)
- 19 frontmatter fields present (H08 pass)
## Anti-Example
INPUT: "Make agent state"
BAD OUTPUT:
```yaml
id: agent_state
kind: runtime_state
title: "State"
quality: 8.0
agent: researcher

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
