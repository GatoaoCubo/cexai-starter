---
kind: quality_gate
id: p11_qg_axiom
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of axiom artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: axiom"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, axiom, P11, P10, governance, immutable, fundamental-truth]
tldr: "Gates for axiom artifacts — immutable fundamental rules that govern a domain permanently."
domain: axiom
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.89
related:
  - p11_qg_law
  - p11_fb_axiom
  - bld_instruction_axiom
  - p11_qg_quality_gate
  - p11_fb_quality_gate
---
## Quality Gate

# Gate: axiom
## Definition
| Field     | Value                                          |
|-----------|------------------------------------------------|
| metric    | immutability rigor + scope boundary precision  |
| threshold | 8.0                                            |
| operator  | >=                                             |
| scope     | all axiom artifacts (P10)                      |
## HARD Gates
All must pass. Failure on any = final score 0.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = axiom invisible to system |
| H02 | id matches `^p10_ax_[a-z][a-z0-9_]+$` | Namespace compliance |
| H03 | id == filename stem | Brain search relies on this |
| H04 | kind == "axiom" | Type integrity |
| H05 | quality == null | Never self-score |
| H06 | All 13 required fields present | Completeness |
| H07 | tags is list, len >= 3 | Searchability minimum |
| H08 | rule field is ONE sentence (no period-separated compound rules) | Atomicity — one axiom, one truth |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty | 1.0 |
| S02 | rationale present with >= 2 distinct reasons | 1.0 |
| S03 | scope names concrete domain boundary (not "everything") | 1.0 |
| S04 | enforcement describes detection mechanism, not just intent | 1.0 |
| S05 | immutable == true field present | 0.5 |
| S06 | body has all 7 required sections | 1.0 |
| S07 | Examples section has >= 2 cases (valid and invalid) | 1.0 |
| S08 | Violations section has >= 1 concrete breach scenario | 1.0 |
| S09 | density_score >= 0.80 | 1.0 |
| S10 | keywords present, len >= 2 | 0.5 |
Weights sum: 9.0. Normalize: divide each by 9.0 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as canonical axiom |
| >= 8.0 | PUBLISH — active governance enforcement |
| >= 7.0 | REVIEW — sharpen rule atomicity or add violation scenarios |
| < 7.0  | REJECT — rule is not immutable, or scope is underdefined |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Axiom required to block active system violation in production |
| approver | p10-chief |
| audit_trail | Log in records/audits/ with violation evidence and timestamp |
| expiry | 24h — axioms must be fully specified before expiry |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples: axiom-builder
## Golden Example
INPUT: "Formalize the CEX rule that quality scores must never be self-assigned"
OUTPUT:
```yaml
id: p10_ax_quality_never_self_scored
kind: axiom
pillar: P10
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
domain: "quality_assurance"
quality: null
tags: [axiom, quality, self-score, integrity, evaluation]
tldr: "No artifact may assign its own quality score; external validation required"
rule: "An artifact producer MUST NOT assign a quality score to its own output"
scope: "All CEX artifacts across all pillars (P01-P12)"
rationale: "Self-scoring creates unfalsifiable feedback loops that erode trust"
enforcement: "HARD gate H05 in every builder rejects quality != null"
immutable: true
priority: 10
dependencies: []
keywords: [quality, self-score, validation, integrity]
linked_artifacts:
  primary: null
  related: [p11_qg_knowledge_card, p11_qg_model_card]
```
## Rule Statement
An artifact producer MUST NOT assign a quality score to its own output.
## Rationale
- Self-scoring creates circular validation — the producer judges itself
- External scoring enables calibration across producers and domains
- Every quality framework (peer review, ISO 9001) separates production from evaluation
## Scope
- Domain: All artifact production in CEX
- System: Every builder, every pillar (P01-P12)
- Layer: Governance (quality gate enforcement)
## Enforcement
- Detection: HARD gate H05 in every quality_gate checks quality == null
- Response: Artifact rejected at publish; builder must output quality: null
## Examples
1. knowledge-card-builder sets quality: null; external reviewer scores 8.5
2. signal-builder emits signal with quality_score from monitor, not from self
## Violations
1. Builder outputs quality: 9.0 on its own artifact
   - Impact: Score inflation, pool contamination, trust erosion
   - Resolution: Reject artifact, re-validate with external scorer

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
