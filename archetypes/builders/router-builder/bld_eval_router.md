---
kind: quality_gate
id: p11_qg_router
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of router artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Router'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: 'Quality gate for task routing logic: verifies route table completeness, confidence
  threshold, fallback reachability, and pattern uniqueness.'
domain: router
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
density_score: 0.85
related:
  - router-builder
  - bld_architecture_router
---
## Quality Gate

## Definition
A router maps task patterns to agents via route table, confidence threshold, and fallback. Every route must have a unique pattern.
Scope: `kind: router`. Not dispatch rules (P02) or lifecycle rules (P09).
## HARD Gates
Failure on any single gate means REJECT regardless of soft score.
| ID  | Predicate | How to test |
|-----|-----------|-------------|
| H01 | Frontmatter parses as valid YAML | `yaml.safe_load(frontmatter)` raises no error |
| H02 | `id` matches namespace `p02_router_*` | `id.startswith("p02_router_")` is true |
| H03 | `id` equals filename stem | `Path(file).stem == id` |
| H04 | `kind` equals literal `router` | string equality check |
| H05 | `quality` is null at authoring time | `quality is None` |
| H06 | All required frontmatter fields present and non-empty | id, kind, pillar, title, version, created, updated, author, domain, tags, tldr all present |
## SOFT Scoring
Score each dimension 0 (absent or fails) to 1 (present and passes). Weights are 0.5 or 1.0.
| #  | Dimension | Weight |
|----|-----------|--------|
| 1  | `density_score` field present and >= 0.80 | 1.0 |
| 2  | Every route has a pattern, destination, and confidence floor documented | 1.0 |
| 3  | Confidence threshold value is justified with a rationale comment | 1.0 |
| 4  | Fallback route is always reachable regardless of input (no conditional fallback) | 1.0 |
| 5  | Load balancing strategy documented if multiple destinations share a pattern | 0.5 |
| 6  | Tags list includes `router` | 0.5 |
**Formula**: `final_score = (sum of score_i * weight_i) / (sum of weight_i) * 10`
Weight total: 9.5. Each dimension contributes proportionally. Score range: 0.0 to 10.0.
## Actions
| Tier | Threshold | Action |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publish to pool as golden; use as reference for routing design |
| PUBLISH | >= 8.0 | Publish to pool; mark production-ready |
| REVIEW | >= 7.0 | Return to author with scored dimension feedback; one revision cycle allowed |
| REJECT | < 7.0 | Block from pool; full rewrite required before re-evaluation |
## Bypass
| Field | Value |
|-------|-------|
| condition | Router covers a domain with fewer than 3 known patterns at design time (bootstrapping phase) |
| approver | Domain lead must approve in writing before bypass takes effect |
| audit_log | Record in `records/pool/audits/bypasses.md` with date, approver, and reason |
| expiry | 21 days from bypass grant; route table must reach >= 3 routes before expiry |

## Examples

# Examples: router-builder
## Golden Example
INPUT: "Create a router for dispatching tasks to CEX directors based on domain"
OUTPUT:
```yaml
id: p02_router_director_task
kind: router
pillar: P02
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
routes_count: 7
fallback_route: "builder_agent"
confidence_threshold: 0.7
domain: "director_dispatch"
quality: 8.9
tags: [router, director, dispatch, P02, multi-agent]
tldr: "Routes incoming tasks to 7 CEX directors by domain pattern matching with 0.7 confidence gate"
timeout_ms: 3000
retry_count: 1
load_balance: "priority"
keywords: [director, dispatch, routing, task-assignment, domain-routing]
density_score: 0.88
```
## Routes
| Pattern | Destination | Priority | Confidence Min | Conditions |
|---------|-------------|----------|----------------|------------|
| research, scrape, competitor, market | research_agent | 90 | 0.7 | - |
| marketing, copy, ads, listing, social | marketing_agent | 90 | 0.7 | - |
| build, code, component, refactor, test | builder_agent | 85 | 0.7 | - |
| knowledge, document, index, embed | knowledge_agent | 80 | 0.7 | - |
| deploy, infra, database, migrate | operations_agent | 85 | 0.8 | requires_auth |
| monetize, course, pricing, funnel | commercial_agent | 80 | 0.7 | - |
| orchestrate, dispatch, spawn, monitor | orchestrator | 95 | 0.9 | admin_only |
## Decision Logic
Algorithm: priority-first with confidence gating.
Each incoming task is scored against all route patterns simultaneously.
Only routes where confidence >= confidence_min are candidates.
Among candidates, highest priority wins. Ties broken by most specific pattern match.
## Fallback
Default destination: builder_agent (general-purpose build director).
Trigger: no route scores above 0.7 confidence.
Behavior: route to builder_agent with metadata flag `routed_by_fallback: true`.
## Escalation
Trigger: two or more routes score within 0.05 confidence of each other.
Action: return both candidates with scores; let orchestrator arbitrate.
Notification: signal `p12_sig_routing_ambiguous` with candidate list.
## Integration
- Receives from: orchestrator, user input
- Routes to: 7 agents (see Routes table)
- Consults: dispatch_rules (P12)
- Signal on failure: `p12_sig_routing_failed`

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p11_qg_quality_gate | sibling | 0.49 |
| [[router-builder]] | upstream | 0.47 |
| [[bld_architecture_router]] | upstream | 0.42 |
