---
kind: quality_gate
id: bld_quality_gate_conformity_assessment
pillar: P11
llm_function: GOVERN
purpose: Hard and soft quality gates for conformity_assessment artifacts
quality: null
title: "Conformity Assessment Builder -- Quality Gate"
version: "1.0.0"
author: wave7_n05
tags: [conformity_assessment, builder, quality_gate]
tldr: "8 hard gates + 5 scored dimensions for EU-AI-Act Annex-IV conformity assessment artifacts"
domain: "conformity_assessment construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [conformity_assessment construction, hard gates, conformity_assessment, builder, quality_gate, quality gate, conformity assessment builder]
density_score: 0.85
related:
  - bld_eval_default
---
## Quality Gate
# Conformity Assessment Builder -- Quality Gate
## Hard Gates (H01-H08)
All 8 gates MUST pass. A single FAIL blocks publication (quality stays null).
| Gate | ID | Check | Pass Condition | FAIL Action |
|------|----|-------|---------------|-------------|
| Frontmatter complete | H01 | YAML frontmatter present with all required fields | All fields populated, quality: null | Add missing fields |
| ID pattern valid | H02 | id matches ^p11_ca_[a-z0-9_]+\.md$ | Regex match | Rename artifact |
| Kind correct | H03 | kind == "conformity_assessment" | Exact match | Fix kind field |
| RMS section present | H04 | risk_management_system object has >= 6 sub-fields | Count >= 6 | Add missing RMS fields |
| Data governance present | H05 | data_governance_plan object has >= 5 sub-fields | Count >= 5 | Add missing DGP fields |
| Human oversight present | H06 | human_oversight_measures object has >= 5 sub-fields | Count >= 5 | Add missing HOM fields |
## Hard Gate Evaluation Script (pseudo-code)
```
results = {}
# H01 -- Frontmatter
required_fields = [system_name, system_version, provider_name, annex_iii_category,
                   article_43_procedure, declaration_date, eu_ai_act_ref,
                   technical_documentation_reference]
results[H01] = all(field in frontmatter for field in required_fields)
```
## Soft Scoring Dimensions (D01-D05)
Total possible score: 10.0. Quality floor: 8.0. Target: 9.0+.
| Dim | ID | Weight | Criterion | Max Points |
|-----|----|--------|-----------|-----------|
| Completeness | D01 | 0.25 | All 7 Annex-IV categories documented with substantive content | 2.5 |
| Regulatory accuracy | D02 | 0.25 | All claims cite specific EU AI Act article + annex section; no misquotations | 2.5 |
| Evidence density | D03 | 0.20 | RMS, DGP, HOM sections contain specific evidence references, not placeholders | 2.0 |
| Traceability | D04 | 0.20 | Each risk control traceable to an Art. 9 risk ID; each data provision traceable to Art. 10 | 2.0 |
| Auditability | D05 | 0.10 | Aug-2026 deadline items flagged; notified body ID present if required; provider contact included | 1.0 |
## Score Computation
Score = D01 + D02 + D03 + D04 + D05. Floor: 8.0. Target: 9.0+.
H-gate FAIL (any) = BLOCK regardless of D score. Fix H-gate first.
## Gate Failure Protocol
| Score Range | Action |
|-------------|--------|
| < 8.0 | Return to F6. Fix H-gates first, then lowest D dimensions. |
| 8.0-8.9 | Publish with quality: null. Flag for next cycle. |
| 9.0-10.0 | Publish. Signal complete. |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
