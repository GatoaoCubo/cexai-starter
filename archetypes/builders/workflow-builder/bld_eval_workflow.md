---
kind: quality_gate
id: p11_qg_workflow
pillar: P12
llm_function: GOVERN
purpose: Golden and anti-examples of workflow artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Workflow'
version: 1.0.0
author: builder
tags:
- eval
- P12
- quality_gate
- examples
tldr: Validates multi-step orchestration flows for steps, dependency ordering, completion
  signals, and recovery.
domain: workflow
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords: [workflow, dependency ordering, steps, execution, signals]
density_score: 0.85
related:
  - p01_kc_workflow
  - bld_knowledge_card_workflow
  - bld_memory_workflow
  - bld_architecture_workflow
  - workflow-builder
---
## Quality Gate

## Definition
A workflow defines a multi-step orchestration: ordered or parallel steps, the agent assigned to each, dependencies between steps, and completion signals. Workflows must be executable by automated runners without human interpretation. This gate ensures every workflow is acyclic, complete, and safe to run end-to-end.
## HARD Gates
Failure on any HARD gate causes immediate REJECT. No score is computed.
| ID  | Check | Rule |
|-----|-------|------|
| H01 | Frontmatter parses | YAML frontmatter is valid and complete with no syntax errors |
| H02 | ID matches namespace | `id` matches pattern `^p12_wf_[a-z][a-z0-9_]+$` |
| H03 | ID equals filename | `id` slug matches the parent directory or filename stem |
| H04 | Kind matches literal | `kind` is exactly `workflow` |
| H05 | Quality is null | `quality` field is `null` (not yet scored) |
| H06 | Required fields present | `steps`, `execution`, `signals` all defined and non-empty |
## SOFT Scoring
Score each dimension 0 or 10. Multiply by weight. Divide total by sum of weights, scale to 0-10.
| Dimension | Weight | Pass Condition |
|-----------|--------|----------------|
| Density >= 0.80 | 1.0 | No prose restating what the steps table shows |
| Steps have agent assignment | 1.0 | Each step names the agent or component responsible |
| Dependency graph is acyclic | 1.0 | No step depends on a step that depends on it |
| Parallel vs sequential explicit | 0.5 | `execution` is set per step or globally |
| Error recovery per step | 1.0 | Each step has `on_failure` (retry, skip, abort, or escalate) |
| Tags include workflow | 0.5 | `tags` contains `"workflow"` |
Sum of weights: 9.0. `soft_score = sum(weight * gate_score) / 9.0 * 10`
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — archive to pool as reference workflow |
| >= 8.0 | PUBLISH — safe for automated execution in production |
| >= 7.0 | REVIEW — runnable but recovery or signal references need work |
| < 7.0 | REJECT — do not run; steps are incomplete or dependencies are ambiguous |
## Bypass
| Field | Value |
|-------|-------|
| condition | Workflow is a one-time migration or incident response procedure that will not be re-run; formal gating would delay the response |
| approver | Lead engineer or on-call responsible for the affected system |
| audit_log | Entry required in `.claude/bypasses/workflow_{date}.md` with the incident or migration ticket ID |
| expiry | Single execution only; workflow must be archived or brought to PUBLISH score before any second run |
H01 (frontmatter parses) and H05 (quality is null) cannot be bypassed under any condition.

## Examples

# Examples: workflow-builder
## Golden Example
INPUT: "Create workflow for research-then-build mission with research_agent and builder_agent"
OUTPUT:
```yaml
id: p12_wf_research_build_mission
kind: workflow
pillar: P12
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
title: "Research Then Build Mission"
steps_count: 3
execution: mixed
directors: [shaka, edison]
timeout: 5400
retry_policy: per_step
depends_on: []
signals: [complete, error]
spawn_configs: [p12_spawn_shaka_solo_research, p12_spawn_edison_solo_build]
domain: "orchestration"
quality: 8.8
tags: [workflow, research, build, multi-director]
tldr: "3-step mixed workflow: research_agent researches, builder_agent builds from findings, orchestrator consolidates"
density_score: 0.90
```
## Purpose
Orchestrates a research-then-build mission where research_agent gathers market intelligence,
builder_agent implements based on findings, and orchestrator consolidates results. Steps 1-2 are
sequential (build depends on research), step 3 runs after both complete.
## Steps
### Step 1: Market Research [shaka]
- **Agent**: shaka (sonnet)
- **Action**: Research target market and produce knowledge cards
- **Input**: research brief from handoff file
- **Output**: 3-5 knowledge cards committed to records/pool/
### Step 2: Implementation [edison]
- **Agent**: edison (opus)
- **Action**: Build feature using research findings from Step 1
- **Input**: knowledge cards produced by research_agent
- **Output**: implemented feature with tests passing
### Step 3: Consolidation [orchestrator]
- **Agent**: orchestrator (opus)
- **Action**: Review outputs, archive handoffs, push to remote
- **Input**: signals from Steps 1-2, git log
- **Output**: consolidated commit, archived handoffs
## Dependencies
- Handoff files must exist for research_agent and builder_agent before workflow starts
- spawn_configs referenced must be valid (p12_spawn_shaka_solo_research, p12_spawn_edison_solo_build)
## Signals
- **On step complete**: {sat}_complete signal emitted (see signal-builder)
- **On workflow complete**: workflow_complete signal with aggregate quality
- **On error**: {sat}_error signal, retry per step (max 1), then escalate to orchestrator
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p12_wf_ pattern (H02 pass)
- kind: workflow (H04 pass)
- 20 required fields present (H06 pass)

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_workflow]] | related | 0.47 |
| [[bld_knowledge_card_workflow]] | upstream | 0.47 |
| [[bld_memory_workflow]] | upstream | 0.46 |
| [[bld_architecture_workflow]] | upstream | 0.42 |
| [[workflow-builder]] | related | 0.42 |
