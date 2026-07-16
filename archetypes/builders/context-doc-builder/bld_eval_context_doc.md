---
kind: quality_gate
id: p11_qg_context_doc
pillar: P11
llm_function: GOVERN
purpose: Golden example and anti-example for context_doc production
quality: null
title: "Gate: context_doc"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, context-doc, P01, prompt-hydration, domain-scope, constraints]
tldr: "Pass/fail gate for context_doc artifacts: domain scope precision, constraint completeness, assumption capture, and hydration readiness."
domain: "domain context documentation — background documents that hydrate prompts with scope, stakeholders, constraints, and assumptions"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.91
related:
  - context-doc-builder
---
## Quality Gate

# Gate: context_doc
## Definition
| Field | Value |
|---|---|
| metric | context_doc artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: context_doc` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | ID contains uppercase, spaces, or invalid chars |
| H03 | ID equals filename stem | `id: my_ctx` but file is `other_ctx.md` |
| H04 | Kind equals literal `context_doc` | `kind: knowledge_card` or `kind: glossary_entry` or any other value |
| H05 | Quality field is null | `quality: 7.0` or any non-null value |
| H06 | All required fields present | Missing `domain`, `scope`, or `constraints` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Scope precision | 1.0 | Domain boundary is specific enough to exclude adjacent domains unambiguously |
| Out-of-scope completeness | 1.0 | Adjacent domains that could be confused are explicitly excluded |
| Constraint actionability | 1.0 | Each constraint is a specific rule a prompt can apply, not a vague guideline |
| Assumption explicitness | 1.0 | Assumptions are stated as assumptions (not facts), with source noted |
| Stakeholder relevance | 0.5 | Stakeholders listed are those whose concerns affect prompt behavior |
| Dependency mapping | 0.5 | External dependencies that constrain the domain are identified |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Context doc for an emerging domain where constraints are still being discovered; used only in internal experiments |
| approver | Domain owner acknowledgment that constraints are provisional |
| audit_trail | Bypass reason and list of known-incomplete constraint areas in frontmatter comment |
| expiry | 7d — context docs for active domains must reach >= 7.0 within one week of first use |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics) |

## Examples

# Examples: context_doc
## Golden Example
```markdown
id: p01_ctx_br_ecommerce_import_regs
kind: context_doc
pillar: P01
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: builder_agent
domain: ecommerce_imports
scope: "Brazilian import regulations for marketplace sellers, 2025-2026 enforcement cycle"
quality: 8.9
tags: [context-doc, ecommerce_imports, brazil, regulation]
tldr: "BR marketplace imports: ICMS 17-20%, NCM code required, Receita Federal DI threshold R$50"
keywords: [icms, ncm, receita_federal, import, brazil, marketplace, tax]
density_score: 0.87
## Scope
In scope: ICMS rates by state, NCM classification requirements, Receita Federal DI thresholds,
marketplace seller obligations under Lei 14.781/2024.
Out of scope: international shipping logistics, payment processing, consumer returns law.
## Background
Brazil levies ICMS (17-20% by state) on all imported goods sold via marketplace.
NCM codes (8-digit Nomenclatura Comum do Mercosul) are mandatory on all listings.
Receita Federal requires Declaraction de Importaction (DI) for shipments > R$50 commercial value.
Lei 14.781/2024 expanded marketplace platform liability for seller tax compliance.
## Stakeholders
- Marketplace seller agents: need tax rates and NCM requirements before listing
- Compliance agents: enforce DI threshold checks pre-shipment
- Pricing agents: require ICMS rates to compute landed cost
## Constraints & Assumptions
- ICMS rates are state-specific; this context uses SP rate (18%) as default
- NCM codes assumed valid per MDIC 2025 table (update required if MDIC revises)
- DI threshold R$50 is current as of 2026-01-01; subject to Receita Federal portaria changes
## Dependencies
- `p01_kc_ncm_classification_rules` — atomic NCM lookup facts
- `p01_kc_icms_state_rates_2025` — per-state rate table
- Receita Federal Portaria RFB 1.073/2025 (external)
## Anti-Example
```markdown
id: ctx_brazil_imports
kind: context_doc
pillar: P01
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: builder_agent
domain: imports
quality: 8.5
tags: [context-doc]
tldr: "This document provides a comprehensive overview of the various regulatory frameworks
that apply to the importation of goods into Brazil through various channels including
ecommerce marketplaces and direct consumer imports."

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
