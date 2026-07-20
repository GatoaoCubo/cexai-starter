---
id: p11_qg_admin_orchestration
kind: quality_gate
pillar: P11
title: "Gate: N07 Orchestration Quality"
version: "1.0.0"
quality: null
tags: [quality-gate, orchestration, validation]
8f: F7_govern
nucleus: n07
domain: orchestration
created: "2026-07-20"
tldr: "Quality gate for orchestration output -- signal received, quality >= 8.0, doctor pass, compile success, git committed, scope respected."
related:
  - p12_ho_n07
  - p12_sig_admin_orchestration
  - p07_bm_dispatch_health_n07
---

# Quality Gate: N07 Orchestration

## Definition

| Property | Value |
|----------|-------|
| Metric | Orchestration output quality |
| Threshold | 8.0 / 10.0 |
| Operator | >= |
| Scope | All artifacts dispatched by the orchestrator to builders |

## Checklist (HARD gates -- ALL must pass)

- [ ] H01: Signal received -- builder emitted completion signal to `.cex/runtime/signals/`
- [ ] H02: Quality score >= 8.0 -- reported by builder in signal payload
- [ ] H03: Git committed -- builder committed changes before signaling
- [ ] H04: Compile success -- `python _tools/cex_compile.py {path}` produces valid YAML
- [ ] H05: Doctor pass -- `python _tools/cex_doctor.py` reports no errors for the artifact
- [ ] H06: Frontmatter valid -- YAML parses, required fields present, kind matches
- [ ] H07: Scope respected -- builder only modified files within the handoff's scope fence

## Scoring (SOFT gates -- weighted dimensions)

| ID | Dimension | Weight | Criteria |
|----|-----------|--------|----------|
| S01 | Completeness | 25% | All handoff tasks completed, no partial deliverables |
| S02 | Density | 20% | High signal-to-filler ratio; no padding prose |
| S03 | Accuracy | 20% | Content matches domain reality, no placeholder data |
| S04 | Structure | 15% | Follows the builder's output template and sections |
| S05 | Integration | 10% | Related-artifact links correct, references resolve |
| S06 | Freshness | 10% | Updated date is current; version bumped on rebuild |

## Scoring Formula

```
aggregate_score = (S01*0.25) + (S02*0.20) + (S03*0.20) + (S04*0.15) + (S05*0.10) + (S06*0.10)
PASS = ALL(H01..H07) AND aggregate_score >= 0.80
```

## Actions

| Outcome | Consequence |
|---------|-------------|
| PASS (all HARD + soft >= 0.80) | Artifact accepted, handoff archived |
| HARD FAIL (any H01-H07 fails) | Block -- builder must fix and re-signal |
| SOFT FAIL (aggregate < 0.80) | Return with feedback -- builder revises |

## Quality Tiers

| Tier | Score | Action |
|------|-------|--------|
| GOLDEN | >= 9.5 | Mark as reference example |
| PUBLISH | >= 8.0 | Standard acceptance |
| REVIEW | >= 7.0 | Revision required |
| REJECT | < 7.0 | Full rebuild |

## Bypass Policy

- **Who may override**: the orchestrator operator only.
- **Conditions**: documented justification required, logged to `.cex/runtime/signals/`.
- **Audit**: bypass events recorded as signals with `status: bypass` and a reason field.

## Validation Commands

```bash
python _tools/cex_compile.py {{artifact_path}}
python _tools/cex_doctor.py
ls .cex/runtime/signals/{{nucleus}}_*.json
```

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| [[p12_ho_n07]] | upstream -- the handoff whose scope fence H07 checks |
| [[p12_sig_admin_orchestration]] | upstream -- the signal H01/H02 read |
| [[p07_bm_dispatch_health_n07]] | sibling -- H05's doctor-pass cadence, measured over time |
