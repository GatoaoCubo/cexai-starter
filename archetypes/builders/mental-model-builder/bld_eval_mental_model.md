---
kind: quality_gate
id: p11_qg_mental_model
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of mental_model artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Mental Model"
version: "1.0.0"
author: builder_agent
tags: [quality-gate, mental-model, routing, P02, cognitive-map]
tldr: "Quality gate for mental_model artifacts: enforces routing rules, decision tree, domain map, and design-time-only scope."
domain: mental_model
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [mental model, enforces routing rules, decision tree, domain map, and design-time-only scope, quality-gate, mental-model]
density_score: 0.85
related:
  - p03_ins_mental_model
  - mental-model-builder
  - p11_qg_runtime_state
  - bld_collaboration_mental_model
  - bld_knowledge_card_mental_model
---
## Quality Gate

# Gate: Mental Model

This ISO operationalizes a mental model -- a compact analogy or abstraction that guides reasoning.
## Definition
A `mental_model` is a design-time cognitive map that tells an agent how to route, prioritize, and decide. It carries no runtime state and executes no logic. Gates here enforce that routing rules have confidence thresholds, decisions have if/then/else structure, and the artifact never encodes live session data — which belongs in runtime state artifacts.
## HARD Gates
All HARD gates must pass. Any single failure sets score to 0 and blocks publish.
| ID  | Check | Failure consequence |
|-----|-------|---------------------|
| H01 | YAML frontmatter parses without error | Artifact unparseable by tooling |
| H02 | `id` matches `^p02_mm_[a-z][a-z0-9_]+$` | Namespace violation — not discoverable |
| H03 | `id` equals filename stem exactly | Brain search failure — id/file mismatch |
| H04 | `kind` == literal string `"mental_model"` | Type integrity failure |
| H05 | `quality` == `null` | Self-scoring violation — pool metric corruption |
| H06 | All required fields present and non-empty (`id`, `kind`, `pillar`, `version`, `created`, `updated`, `author`, `agent`, `domain`, `routing_rules`, `decision_tree`, `tags`, `tldr`) | Incomplete artifact |
## SOFT Scoring
Weights sum to 100%. Each dimension scores 0 or its full weight.
| ID  | Dimension | Weight | Criteria |
|-----|-----------|--------|----------|
| S01 | tldr quality | 1.0 | `tldr` <= 160 chars, names the agent and its primary routing concern |
| S02 | Routing rules have confidence thresholds | 1.0 | Each rule specifies a match confidence or keyword specificity level |
| S03 | Decisions have if/then/else structure | 1.0 | Decision tree entries follow: condition → then action → else action |
| S04 | Priorities ordered with rationale | 1.0 | `priorities` list is ranked and each rank has a one-line justification |
| S05 | Heuristics testsble | 0.5 | Each heuristic can be verified with a specific input example |
| S06 | Domain boundaries explicit | 1.0 | Domain Map states what the agent covers AND what it routes away |
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool + record in memory |
| >= 8.0 | PUBLISH | Commit to pool |
| >= 7.0 | REVIEW | Acceptable with documented improvement items |
| < 7.0 | REJECT | Revise and resubmit — do not publish |
| 0 (HARD fail) | REJECTED | Fix failing HARD gate(s) first |
## Bypass
Bypasses are logged and expire automatically.
| Field | Value |
|-------|-------|
| condition | New agent bootstrapping — routing rules are provisional and under observation from live sessions |

## Examples

# Examples: mental-model-builder

This ISO operationalizes a mental model -- a compact analogy or abstraction that guides reasoning.
## Golden Example
INPUT: "Create mental model for a content-reviewer agent"
OUTPUT:
```yaml
id: p02_mm_content_reviewer
kind: mental_model
pillar: P02
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
agent: "content-reviewer"
```
## Agent Reference
content-reviewer: reviews content for compliance, accuracy, density, and language quality.
## Routing Rules
| Keywords | Action | Confidence |
|----------|--------|------------|
| review, audit, check, validate | execute quality review pipeline | 0.9 |
| grammar, spelling, typo, language | run language quality checks | 0.85 |
| compliance, legal, policy, brand | apply compliance ruleset | 0.8 |
| improve, rewrite, enhance, optimize | route to content-writer agent | 0.7 |
## Decision Tree
1. IF content has compliance flags THEN prioritize compliance ELSE start with language
2. IF quality score < 7.0 THEN reject with failures ELSE approve with annotation
3. IF content > 5000 words THEN split and review each section
WHY THIS IS GOLDEN:
- quality: null (H05 pass) | id p02_mm_ pattern (H02 pass) | kind: mental_model (H04 pass)
- pillar: P02 (H07 pass) | 23 fields (H06 pass) | 4 routing rules (H08 pass)
- 3 decision conditions (H09 pass) | priorities: 5 items (S03 pass)
- heuristics: 3 items (S04 pass) | domain_map with covers+routes_to (S05 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
