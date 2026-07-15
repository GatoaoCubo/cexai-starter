---
id: rule_raci_matrix
kind: runtime_rule
pillar: P02
title: "CEX Nuclei RACI Matrix"
version: 1.0.0
created: 2026-04-27
quality: null
density_score: 0.92
tags: [raci, nuclei, governance, role_clarity]
related:
  - n07-orchestrator
  - composable-crew
  - p02_agent_admin_orchestrator
---

## RACI Matrix

| Action | N01 | N02 | N03 | N04 | N05 | N06 | N07 |
|--------|-----|-----|-----|-----|-----|-----|-----|
| Build artifact | C | C | **R** | C | C | C | A |
| Dispatch wave | C | C | E | C | C | C | **R/A** |
| Score quality | I | I | E | E | **R** | I | A |
| Deploy / ship | I | I | E | I | **R** | I | A |
| Brand decisions | I | E | I | I | I | **R** | A |
| Monetize | I | I | I | I | I | **R** | A |
| Research / analyze | **R** | I | I | C | I | I | A |
| Document / KC | I | C | C | **R** | I | I | A |
| Audit / govern | C | I | C | C | E | I | **R/A** |

Legend: **R**=Responsible -- **A**=Accountable -- **C**=Consulted -- **I**=Informed -- **E**=Executes

## Explicit Prohibitions

- **N07** NEVER builds artifacts (route to N03)
- **N03** NEVER scores its own work (peer review only)
- **N04** NEVER overwrites memory facts without versioning
- **N05** NEVER negotiates quality criteria (gate is gate)
- **N02** NEVER fabricates customer data (sources required)
- **N01** NEVER skips at-least-2 alternatives in analysis
- **N06** NEVER prices without market research (N01 dependency)

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| n07-orchestrator | upstream | 0.60 |
| composable-crew | related | 0.50 |
| p02_agent_admin_orchestrator | related | 0.45 |
| 8f-reasoning | related | 0.40 |
| guided-decisions | related | 0.35 |
