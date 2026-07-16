---
kind: quality_gate
id: p11_qg_dispatch_rule
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of dispatch_rule artifacts
pattern: few-shot learning for keyword-to-agent_group routing rules
quality: null
title: "Gate: dispatch_rule"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, dispatch-rule, routing, keyword-mapping, P11]
tldr: "Gates for dispatch_rule artifacts: validates keyword coverage, agent_group enum, fallback logic, multilingual support, and confidence thresholds."
domain: "dispatch_rule — routing rules mapping keywords to agent_groups with fallback logic"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.92
related:
  - dispatch-rule-builder
---
## Quality Gate

# Gate: dispatch_rule
## Definition
| Field     | Value |
|-----------|-------|
| metric    | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator  | AND (all HARD) + weighted_sum (SOFT) |
| scope     | All artifacts where `kind: dispatch_rule` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID  | Check | Failure message |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p12_dr_[a-z][a-z0-9_]+$` | "ID fails dispatch_rule namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"dispatch_rule"` | "Kind is not 'dispatch_rule'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, domain, agent_group, model, priority, keywords, confidence_threshold, fallback, version, created, author, tags | "Missing required field(s)" |
| H07 | `agent_group` value is one of the defined agent_group enum (researcher, marketer, builder, knowledge-engine, executor, monetizer) | "Agent_group not in allowed enum" |
| H08 | `keywords` list is non-empty (>= 3 entries) | "Keyword list must have at least 3 entries" |
| H09 | `confidence_threshold` is a float between 0.0 and 1.0 | "Confidence threshold out of range [0.0, 1.0]" |
| H10 | `fallback` is defined and references a valid agent_group or literal `human` | "Fallback target undefined or invalid" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Keyword breadth | 1.0 | Keywords cover the full semantic space of the domain scope |
| Multilingual coverage | 1.0 | EN keywords required; community language keywords (PT, etc.) present |
| Priority rationale | 0.5 | Priority level (high/medium/low) explained or evident from domain |
| Confidence threshold calibration | 1.0 | Threshold value apownte for domain (not too strict/loose) |
| Fallback chain quality | 1.0 | Fallback agent_group is a logical second-choice for the domain |
| Scope fence clarity | 1.0 | What the rule does NOT route is explicitly stated |
| Model selection rationale | 0.5 | Model choice (sonnet/opus) justified by task complexity |
| Keyword specificity | 1.0 | No overly generic keywords that would cause routing collisions |
| Trigger phrase examples | 1.0 | 2+ example trigger sentences that would activate this rule |
| Boundary vs other rules | 0.5 | Non-overlap with adjacent dispatch rules documented |
| Domain precision | 1.0 | Domain field accurately describes the routing scope |
| Documentation | 0.5 | tldr captures routing intent in <= 160 characters |
Weight sum: 1.0+1.0+0.5+1.0+1.0+1.0+0.5+1.0+1.0+0.5+1.0+0.5 = 10.0 (100%)
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0  | REJECT | Return to author with failure report |
## Bypass
| Field | Value |
|-------|-------|
| conditions | New agent_group being piloted without full keyword corpus established |
| approver | Routing system owner approval required (written) |
| audit_trail | Bypass logged to `records/audits/dispatch_rule_bypass_{date}.md` |
| expiry | 24h; routing rules in active use must be validated quickly |

## Examples

# Examples: dispatch-rule-builder
## Golden Example
INPUT: "Route research, market analysis and competitor scraping to researcher"
OUTPUT (`p12_dr_research.yaml`):
```yaml
id: p12_dr_research
kind: dispatch_rule
pillar: P12
version: 1.0.0
created: 2026-03-26
updated: 2026-03-26
author: codex
domain: research
quality: null
tags: [dispatch, research, shaka, market, scrape]
tldr: Route market research and competitor analysis tasks to researcher agent_group
scope: research
keywords: [researchr, research, market, market, competitor, competitor, scrape, analysis, analysis, benchmark]
agent_group: shaka
model: sonnet
priority: 8
confidence_threshold: 0.70
fallback: pytha
conditions:
  exclude_domains: [internal_docs, knowledge_indexing]
load_balance: false
routing_strategy: hybrid
# research Dispatch Rule
## Purpose
Routes market research, competitor intelligence, and scraping to researcher.
researcher carries firecrawl MCP and research-optimized prompting.
## Keyword Rationale
Bilingual PT/EN coverage fires on both Portuguese operator commands and English
task descriptions. `analysis`/`analysis` catch adjacent sub-tasks.
## Fallback Logic
knowledge-engine handles knowledge domain when researcher is unavailable; can index and
summarize research outputs without firecrawl.
```
WHY THIS IS GOLDEN:
- filename `p12_dr_research.yaml` follows naming pattern
- `id: p12_dr_research` matches `^p12_dr_[a-z][a-z0-9_]+$`
- `kind: dispatch_rule`, `pillar: P12` present
- `quality: null` — never a score at authoring time

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` populated (3-15), 1+ upstream, 1+ downstream
- Penalty: -0.3 if empty

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[dispatch-rule-builder]] | downstream | 0.44 |
