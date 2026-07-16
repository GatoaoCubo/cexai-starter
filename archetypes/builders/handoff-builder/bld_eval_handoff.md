---
kind: quality_gate
id: p11_qg_handoff
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of handoff artifacts
pattern: few-shot learning for delegation instruction packaging
quality: null
title: "Gate: Handoff"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, handoff, delegation, orchestration, scope-fence]
tldr: "Gates ensuring handoff artifacts carry complete delegation context: task, scope fence, commit instructions, and size discipline."
domain: "handoff — task delegation packages for agent_group execution"
created: "2026-03-27"
updated: "2026-03-27"
last_reviewed: "2026-04-18"
8f: "F7_govern"
density_score: 0.88
related:
  - handoff-builder
---
## Quality Gate

# Gate: Handoff
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: handoff` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error on any field |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | Uppercase, spaces, or leading digit |
| H03 | ID equals filename stem | `id: deploy_api` in file `setup.md` |
| H04 | Kind equals literal `handoff` | Any other kind value |
| H05 | Quality field is `null` | Any non-null value |
| H06 | All required fields present | Missing: task, context, scope_fence, commit, or signal |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Task decomposition | 1.0 | Steps are atomic and independently verifiable | Steps exist but some are compound | Single block of instructions |
| S02 | Context completeness | 1.0 | Background, motivation, and prior state all present | Partial context (2/3) | Context absent |
| S03 | Scope fence precision | 1.0 | Exact paths listed in both allowed and prohibited | Paths listed for one side only | Vague scope description |
| S04 | Commit instruction quality | 0.5 | Stage command + message template + signal command present | Only commit message present | No commit guidance |
| S05 | Signal instruction | 0.5 | Signal call with agent_group, status, and score specified | Signal mentioned without params | Signal absent |
| S06 | Step ordering | 1.0 | Dependencies between steps are explicit | Steps ordered but implicit deps | Steps unordered |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to pool as golden handoff template |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|
| Conditions | Time-critical incident response where full context is not yet known |
| Approver | Senior orchestrator (human) only |

## Examples

# Examples: handoff-builder
## Golden Example
INPUT: "Create handoff for edison to build 3 archetype builders in wave 19"
OUTPUT (`p12_ho_wave19_builders.md`):
```yaml
id: p12_ho_wave19_builders
kind: handoff
lp: P12
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "stella"
agent_group: "edison"
```
# builder_agent — WAVE19: Build 3 Builders
**Full Autonomy** | **Quality 9.0+**
**REGRA: Commit and signal ANTES de qualquer pausa.**
## Context
Wave 19 requires 3 new archetype builders for types session_state (P10),
dag (P12), and handoff (P12). Each builder follows the 13-ISO pattern
established by _builder-builder. Reference builders: signal-builder, workflow-builder.
## Tasks
### Step 1: Read References
Read _builder-builder/BUILDER_NORMS.md, signal-builder/, and workflow-builder/.
### Step 2: Build session-state-builder
Create 13 builder spec files in archetypes/builders/session-state-builder/.
### Step 3: Commit session-state-builder
Run: git add archetypes/builders/session-state-builder/
Run: git commit -m "[N03] session-state-builder"
### Step 4: Build dag-builder
Create 13 builder spec files in archetypes/builders/dag-builder/.
### Step 5: Commit dag-builder
Run: git add archetypes/builders/dag-builder/
Run: git commit -m "[N03] dag-builder"
### Step 6: Build handoff-builder
Create 13 builder spec files in archetypes/builders/handoff-builder/.
### Step 7: Commit handoff-builder
Run: git add archetypes/builders/handoff-builder/
Run: git commit -m "[N03] handoff-builder"
## Scope Fence
- SOMENTE: archetypes/builders/session-state-builder/, archetypes/builders/dag-builder/, archetypes/builders/handoff-builder/
- NAO TOQUE: archetypes/builders/_builder-builder/, archetypes/builders/signal-builder/, P12_orchestration/_schema.yaml
## Commit
```bash
git add archetypes/builders/session-state-builder/
git commit -m "archetype: session-state-builder -- 13 ISO (P10, Wave 19)"
git add archetypes/builders/dag-builder/
git commit -m "archetype: dag-builder -- 13 ISO (P12, Wave 19)"
git add archetypes/builders/handoff-builder/
git commit -m "archetype: handoff-builder -- 13 ISO (P12, Wave 19)"
```
## Signal
```bash
python -c "from records.core.python.signal_writer import write_signal; write_signal('edison', 'complete', 9.0)"
```
WHY GOLDEN: filename `p12_ho_*`, 19+ frontmatter fields, all 5 body sections, specific tasks, SOMENTE+NAO TOQUE, exact git commands, signal mechanism, no prompt/event/routing drift.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
