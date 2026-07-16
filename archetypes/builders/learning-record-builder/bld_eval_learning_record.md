---
kind: quality_gate
id: p11_qg_learning_record
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of learning_record artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Learning Record"
version: "1.0.0"
author: builder_agent
tags: [quality-gate, learning-record, experience-capture, P10, retrospective]
tldr: "Quality gate for learning_record artifacts: enforces outcome classification, impact score, and reproducible context."
domain: learning_record
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.85
---
## Quality Gate

# Gate: Learning Record
## Definition
A `learning_record` captures a discrete experience — a pattern that worked or an anti-pattern that failed — with enough context to reproduce the outcome. Gates prevent vague retrospectives from entering the pool and ensure every record carries a scored, classified, reproducible finding.
## HARD Gates
All HARD gates must pass. Any single failure sets score to 0 and blocks publish.
| ID  | Check | Failure consequence |
|-----|-------|---------------------|
| H01 | YAML frontmatter parses without error | Artifact unparseable by tooling |
| H02 | `id` matches `^p10_lr_[a-z][a-z0-9_]+$` | Namespace violation — not discoverable |
| H03 | `id` equals filename stem exactly | Brain search failure — id/file mismatch |
| H04 | `kind` == literal string `"learning_record"` | Type integrity failure |
| H05 | `quality` == `null` | Self-scoring violation — pool metric corruption |
| H06 | All required fields present and non-empty (`id`, `kind`, `pillar`, `version`, `created`, `updated`, `author`, `topic`, `outcome`, `impact`, `agent_group`, `tags`, `tldr`) | Incomplete artifact |
## SOFT Scoring
Weights sum to 100%. Each dimension scores 0 or its full weight.
| ID  | Dimension | Weight | Criteria |
|-----|-----------|--------|----------|
| S01 | tldr quality | 1.0 | `tldr` <= 160 chars, non-empty, states the finding not just the topic |
| S02 | Context sufficient for reproduction | 1.0 | Names environment, timing, and triggering conditions |
| S03 | Pattern steps concrete | 1.0 | Pattern section has >= 2 ordered steps, not abstract principles |
| S04 | Anti-pattern failure specific | 1.0 | Anti-Pattern section names exact failure mode, not category |
| S05 | Impact score justification clear | 1.0 | Score justified with measurable delta (time, errors, quality) |
| S06 | Actionable takeaway present | 1.0 | Closes with a single directive another agent can act on immediately |
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

## Examples

# Examples: learning-record-builder
## Golden Example
INPUT: "Document the learning from continuous batching achieving 1.6x speedup with 3 agent_groups"
OUTPUT:
```yaml
id: p10_lr_continuous_batching_speedup
kind: learning_record
pillar: P10
version: "1.0.0"
created: "2026-03-05"
updated: "2026-03-05"
author: "builder"
domain: "orchestration"
quality: 8.8
tags: [learning, continuous-batching, speedup, orchestration, multi-agent_group]
tldr: "Continuous batching with 3 sats achieved 1.6x speedup; task complexity drives speed, not model tier"
topic: "Continuous batching multi-agent_group performance"
outcome: SUCCESS
score: 9.0
context: "ISOFIX mission, 7 batches across researcher+builder+knowledge-engine, 2026-03-05"
agent_group: "orchestrator"
reproducibility: HIGH
impact: "1.6x throughput increase, zero git lock contention at 3 agent_groups"
timestamp: "2026-03-05T14:30:00Z"
dependencies: []
keywords: [batching, parallel, throughput, spawn, grid]
linked_artifacts:
  primary: null
  related: [p12_spawn_grid, p08_pat_continuous_batching]
```
## Summary
Continuous batching with 3 agent_groups (researcher+builder+knowledge-engine) achieved 1.6x speedup over sequential execution. Speed was driven by task complexity, not model tier — opus finished faster than sonnet on simpler tasks. Zero git lock contention observed.
## Pattern
- Use spawn_grid.ps1 with -mode continuous for >6 tasks
- Name handoffs as {MISSION}_batch_{N}_{DOMAIN}.md for queue management
- Limit to 3 concurrent agent_groups (RAM ceiling at 4+)
- Let queue auto-refill slots as agent_groups complete
## Anti-Pattern
- Running >3 agent_groups causes BSOD risk (RAM exhaustion)
- Assuming opus is slower than sonnet — speed depends on task, not model
- Manual slot management instead of auto-refill wastes idle time
## Context
- Environment: Windows 10 Pro, 32GB RAM, 3 Claude Code terminals
- Agent_group: orchestrator orchestrating researcher+builder+knowledge-engine
- Timing: 2026-03-05, ISOFIX mission, 7 sequential batches
- Constraints: max 3 terminals (BSOD prevention), 5s spawn delay
## Impact
- 1.6x throughput vs sequential single-agent_group execution
- Zero git lock contention across 3 concurrent committers
- Queue auto-refill eliminated idle time between waves
## Reproducibility
- Conditions: 3 agent_groups, >6 tasks, independent work units
- Confidence: HIGH (tested on ISOFIX 7/7 and CBTEST mixed)
- Caveats: tasks must be independent; shared file edits cause conflicts

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
