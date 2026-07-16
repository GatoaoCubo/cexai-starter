---
kind: quality_gate
id: p11_qg_action_paradigm
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for action_paradigm artifacts
quality: null
title: "Quality Gate: Action Paradigm"
version: "1.0.0"
author: n02_reviewer
tags: [action_paradigm, builder, quality_gate, P11]
tldr: "Quality gate for action execution paradigm artifacts defining state-action mappings, preconditions, and failure recovery."
domain: "action_paradigm construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [action_paradigm construction, quality gate, action paradigm, and failure recovery, action_paradigm, builder, quality_gate]
density_score: 0.88
related:
  - action-paradigm-builder
  - bld_memory_action_paradigm
---
## Quality Gate
## Definition
An `action_paradigm` artifact defines how an autonomous agent translates high-level goals
into executable actions within dynamic environments. It specifies state-action mappings,
preconditions, postconditions, failure recovery, and concurrency rules -- not runtime
performance metrics.
Scope: files with `kind: action_paradigm`. Does NOT apply to agent definitions (agent),
workflow sequences (workflow), or tool wrappers (cli_tool).
## HARD Gates
Failure on any single gate means REJECT regardless of soft score.
| ID  | Predicate | How to test |
|-----|-----------|-------------|
| H01 | Frontmatter parses as valid YAML | `yaml.safe_load(frontmatter)` raises no error |
| H02 | `id` matches namespace `p04_act_*` | `id.startswith("p04_act_")` is true |
| H03 | `id` equals filename stem | `Path(file).stem == id` |
| H04 | `kind` equals literal `action_paradigm` | string equality check |
| H05 | `quality` is null at authoring time | `quality is None` |
| H06 | All required frontmatter fields present and non-empty | id, kind, pillar, title, version, created, updated, author, domain, tags, tldr all present |
## SOFT Scoring
Score each dimension 0 (absent or fails) to 1 (present and passes). Weights are 0.5 or 1.0.
| #  | Dimension | Weight |
|----|-----------|--------|
| 1  | `density_score` field present and >= 0.80 | 1.0 |
| 2  | Action space explicitly defined (discrete, continuous, or symbolic classification) | 1.0 |
| 3  | Failure recovery or error handling mechanism documented | 1.0 |
| 4  | State transition logic present (preconditions + postconditions) | 1.0 |
| 5  | Execution model specified (reactive, deliberative, or hybrid) | 0.5 |
| 6  | Concurrency rules or conflict resolution documented | 0.5 |
**Formula**: `final_score = (sum of score_i * weight_i) / (sum of weight_i) * 10`
Weight total: 9.0. Score range: 0.0 to 10.0.
## Actions
| Tier | Threshold | Action |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publish to pool; add to curated paradigm library |
| PUBLISH | >= 8.0 | Publish to pool; mark production-ready |
| REVIEW | >= 7.0 | Return to author with scored dimension feedback; one revision cycle |
| REJECT | < 7.0 | Block from pool; full rewrite required |
## Bypass
| Field | Value |
|-------|-------|
| condition | Paradigm is a one-off proof-of-concept with documented lifespan under 30 days |
| approver | Domain lead must approve in writing |
| audit_log | Record in `records/pool/audits/bypasses.md` with date, approver, reason |
| expiry | 30 days from bypass grant; paradigm must be retired or brought to full compliance |
## Properties
| Property | Value |
|----------|-------|
| Kind | `quality_gate` |
| Pillar | P11 |
| Domain | action_paradigm construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
## Examples
## Evaluation Criteria
| Dimension | Floor | Target | How to Measure |
|-----------|-------|--------|---------------|
| action_type declared | required | explicit enum value | present in frontmatter or section header |
| preconditions per action | >=1 | >=2 | count guard conditions per action entry |
| postconditions per action | >=1 | >=2 | count state-change assertions per action |
| failure recovery present | required | per-action | at least one fallback per action defined |
| concurrency model | required | explicit | conflict resolution policy stated |
| state machine completeness | >=80% | 100% | all reachable states have transitions |
## Paradigm Type Reference
| Type | Decision Latency | Planning Horizon | Best For |
|------|-----------------|-----------------|----------|
| Reactive | <10ms | None (sensor-direct) | Safety-critical real-time systems |
| Deliberative | 100ms-10s | Full plan before act | Complex goal-directed tasks |
| Hybrid | 10-100ms | Short lookahead | Robots, game agents, autonomous vehicles |
| Hierarchical | Variable per layer | Per abstraction level | Multi-goal, multi-agent coordination |
---
## Golden Example 1: Reactive Autonomous Navigation
```markdown
---
id: p04_act_autonomous_nav_v1
kind: action_paradigm
title: "Reactive Navigation for Mobile Robot"
paradigm_type: reactive
version: 1.0.0
---
```
---
## Golden Example 2: Deliberative Content Moderation Agent
```markdown
---
id: p04_act_content_mod_v2
kind: action_paradigm
title: "Deliberative Content Moderation Paradigm"
paradigm_type: deliberative
version: 2.1.0
---
```
---
## Golden Example 3: Hybrid Game Agent
```markdown
---
id: p04_act_game_agent_v1
kind: action_paradigm
title: "Hybrid FPS Game Agent Paradigm"
paradigm_type: hybrid
version: 1.0.0
---
```
---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
