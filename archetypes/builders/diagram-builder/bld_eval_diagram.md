---
pillar: P11
id: p11_qg_diagram
kind: quality_gate
builder: diagram-builder
version: "1.0.0"
quality: null
title: "Gate: diagram"
author: "builder_agent"
tags: [quality-gate, diagram, architecture-visualization, mermaid, ascii, P11]
tldr: "Gates for diagram artifacts: validates notation correctness, layer boundaries, legend presence, and structural accuracy of architecture visuals."
domain: "diagram — visual architecture representations in ASCII or Mermaid notation"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.90
llm_function: GOVERN
related:
  - bld_architecture_diagram
---
## Quality Gate

# Gate: diagram
## Definition
| Field     | Value |
|-----------|-------|
| metric    | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator  | AND (all HARD) + weighted_sum (SOFT) |
| scope     | All artifacts where `kind: diagram` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID  | Check | Failure message |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p08_diag_[a-z][a-z0-9_]+$` | "ID fails diagram namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"diagram"` | "Kind is not 'diagram'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, domain, notation, subject, layers, version, created, author, tags | "Missing required field(s)" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Layer boundaries | 1.0 | Distinct system layers are visually separated and labeled |
| Legend present | 1.0 | Symbol/notation key included (especially for ASCII) |
| Component completeness | 1.0 | All major system components visible in diagram |
| Data flow direction | 1.0 | Arrows or connections show clear data/control flow |
| Annotation quality | 0.5 | Key components have short inline annotations |
| Boundary clarity | 0.5 | Explicitly not component_map (data) or pattern (prescription) |
Weight sum: 1.0+1.0+1.0+1.0+0.5+0.5+1.0+1.0+1.0+1.0 = 9.0 -> normalize to 100%
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
| conditions | Work-in-progress diagram during active system design iteration |
| approver | Architecture lead sign-off required |
| audit_trail | Bypass event logged to `records/audits/diagram_bypass_{date}.md` |
| expiry | 48h; must reach >= 7.0 before being referenced in documentation |
| never_bypass | H01 (YAML parse failure), H05 (quality null invariant), H08 (empty diagram has no value) |

## Examples

# diagram-builder — EXAMPLES
## Golden Example
INPUT: "Visualize the CEX agent_group orchestration architecture"
FRONTMATTER (19 fields):
```yaml
id: p08_diag_agent_group_orchestration
kind: diagram
pillar: P08
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
domain: "orchestration"
```
## Scope
CEX agent_group orchestration: how orchestrator dispatches tasks to 6 domain agent_groups, monitors progress via signals, and consolidates results. System-level view — not individual agent_group internals.
## Diagram
```text
          ┌─────────┐
          │ orchestrator  │ (orchestrator)
          └────┬────┘
               │ handoffs
    ┌──┬──┬────┼────┬──┬──┐
    ▼  ▼  ▼    ▼    ▼  ▼  ▼
 [researcher][marketer][builder][knowledge-engine][executor][monetizer]
    └──┴──┴────┬────┴──┴──┘
```
## Legend
- `┌──────┐` = system component
- `▼` / `│` = control/data flow direction
- Solid lines = direct communication channel
- Names inside boxes = component identity + domain
## Components
| Component | Role | Layer |
|-----------|------|-------|
| orchestrator | Orchestrator — decomposes, dispatches, monitors | orchestration |
| researcher/marketer/builder/knowledge-engine/executor/monetizer | Domain agent_groups (6) | execution |
| Signal Bus | Event transport — complete/error signals | infrastructure |
| Brain | Knowledge retrieval — BM25 + FAISS | infrastructure |
## Connections
| From | To | Type | Data |
|------|-----|------|------|
| orchestrator | agent_groups | handoff | task + seeds |
| agent_groups | Signal Bus | signal | status + score |
| Signal Bus | orchestrator | poll | completion |
| Brain | all | query | retrieval |
## Annotations
- Max 3 concurrent agent_groups (RAM limit — BSOD if >4)
- Signal poll: 15s

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
