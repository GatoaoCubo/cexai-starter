---
kind: quality_gate
id: p11_qg_skill
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of skill artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Skill'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: Gates ensuring skill files define a specific trigger, two or more typed workflow
  phases, and phase-level error handling without claiming agent identity.
domain: skill
created: '2026-03-27'
updated: '2026-03-27'
last_reviewed: '2026-04-18'
8f: "F7_govern"
keywords: [skill-builder/..., skill, quality, quality gate, gates
failure, workflow phases, scoring
dimensions, spec contains, input output, output typed]
density_score: 0.85
related:
  - skill-builder
  - bld_architecture_skill
  - bld_collaboration_skill
  - p03_ins_skill_builder
  - bld_knowledge_card_skill
---
## Quality Gate

## Definition
A skill is a reusable capability: a named sequence of phases invoked by a trigger and composed with other skills. Passes when trigger is specific, each phase has typed I/O, error handling is per-phase, and the skill makes no agent identity claims.
## HARD Gates
Failure on any HARD gate = immediate REJECT regardless of score.
| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML with no syntax errors | Unparseable file cannot be indexed or validated |
| H02 | `id` matches the file's directory namespace (`skill-builder/...`) | Mismatched IDs cause routing failures |
| H03 | `id` value equals the filename stem (slug portion) | Filename and ID must be the same addressable key |
| H04 | `kind` is exactly `skill` (literal match, no variation) | Kind drives the loader; wrong literal silently misroutes |
| H05 | `quality` field is `null` (not filled by author) | Quality is assigned by this gate, not self-reported |
| H06 | All required frontmatter fields present: id, kind, pillar, title, version, created, updated, author, domain, tags, tldr | Incomplete frontmatter breaks downstream consumers |
## SOFT Scoring
Dimensions are weighted; total normalized weight = 100%.
| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | density >= 0.80 (content per token ratio) | 1.0 | Padded with filler prose | Mostly substantive | No filler; every sentence carries information |
| 2 | Trigger is specific not generic (trigger will not fire on unrelated inputs) | 1.0 | Generic keyword like "do" or "run" | Moderately specific | Exact slash command or narrow keyword pattern with exclusion rules |
| 3 | Phases have clear boundaries (entry condition, exit condition, and handoff artifact per phase) | 1.0 | Phases blend together | Start/end noted | Explicit entry condition, exit condition, and handoff artifact per phase |
| 4 | Input/output typed per phase (not just final output typed) | 1.0 | Only final output typed | Partial typing | Every phase has named fields with types for both input and output |
| 5 | user_invocable flag correct (`true` if user can trigger it, `false` if internal-only) | 0.5 | Missing | Present but unchecked | Present and verified against trigger type |
| 6 | Tags include `skill` | 0.5 | Missing | Present but misspelled | Exactly `skill` in tags list |

## Examples

# Examples: skill-builder
## Golden Example
INPUT: "Create skill for committing and pushing git changes"
OUTPUT:
```yaml
id: p04_skill_git_commit
kind: skill
pillar: P04
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
name: "Git Commit and Push"
```
## Purpose
Provides a safe, validated git commit-and-push workflow reusable across agents and users.
Exists as a skill (not action_prompt) because it has multi-phase lifecycle with validation
and is invoked in dozens of different agent contexts.
## Workflow Phases
## Golden Example 2 (Production — OpenClaude Simplify Skill)
INPUT: "Create skill for parallel code review with 3 agents"
OUTPUT: Reference artifact `P04_tools/compiled/p04_skill_simplify.yaml`

Key patterns from this production skill:
1. **Parallel agent dispatch**: Three independent review agents run concurrently,
   each with a distinct focus (Reuse, Quality, Efficiency).
2. **Enumerated checklist per agent**: Each agent has a numbered list of specific
   things to look for — not vague guidance but concrete patterns (e.g., "N+1 patterns",
   "TOCTOU anti-pattern", "stringly-typed code").
3. **Aggregation phase**: After parallel agents complete, results are aggregated
   and issues are fixed directly — not just reported.
4. **when_to_use / when_not_to_use**: Clear boundary conditions for activation.

WHY THIS IS GOLDEN:
- 3 phases (identify, dispatch parallel, aggregate+fix)
- Each parallel agent has typed focus area with 7 specific checks
- Skill ACTS on findings (fixes issues) not just reports them
- Trigger is clear: /simplify slash command

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
