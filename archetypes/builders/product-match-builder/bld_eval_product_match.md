---
kind: quality_gate
id: p11_qg_product_match
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of product_match artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: product_match"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, product-match, P04, record-linkage, catalog-audit, confidence-floor]
tldr: "Pass/fail gate for product_match artifacts: input contract coverage, output-section fidelity to MOLD_PRODUCT_MATCH, match-engine honesty, and the named match_confiavel gate."
domain: "visual record-linkage / catalog-audit spec definition -- a supplier-item x marketplace-listing matcher with a composite non-key join and an offline catalog audit"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F7_govern"
keywords: [visual record-linkage, catalog audit spec definition, input contract coverage, output section fidelity, match engine honesty, named gate match_confiavel]
density_score: 0.90
related:
  - bld_schema_product_match
---
## Quality Gate

# Gate: product_match
## Definition
| Field | Value |
|---|---|
| metric | product_match artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: product_match` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p04_pm_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, missing prefix, or spaces |
| H03 | ID equals filename stem | `id: p04_pm_supplier_ml` but file is `p04_pm_supplier_amz.md` |
| H04 | Kind equals literal `product_match` | `kind: tool` or `kind: catalog_audit` or any other value |
| H05 | Quality field is null | `quality: 8.5` or any non-null value |
| H06 | All required fields present | Missing any of: match_join_keys, match_engine, match_confidence_floor |
| H07 | Output sections match `MOLD_PRODUCT_MATCH` order+layout | Missing, reordered, or re-layouted section (must be table/list/fields/fields) |
| H08 | EAN/GTIN/barcode never documented as an active join key | `match_join_keys` includes `ean`/`gtin`/`barcode` without an exclusion note |
| H09 | match_engine is one of the 4 closed-enum values | Any value outside {reverse_image, embedding, manual, none} |
| H10 | Veredito section carries the named gate `match_confiavel` | Gate name absent, renamed, or blocker list omitted |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Input contract coverage | 1.5 | All 6 dashboard fields documented with type/required/default; internal `match_exclude_keys` override noted |
| Output section fidelity | 1.5 | Each of the 4 sections has the exact columns/keys from `MOLD_PRODUCT_MATCH` |
| Match-engine honesty | 1.0 | Implementation status per enum value stated accurately (none = only distinct behavior today) |
| Confidence-floor declared | 1.0 | `match_confidence_floor` present and its role in the SIM/PARCIAL/NAO split explained |
| Join-key exclusion documented | 1.0 | `match_exclude_keys` default + rationale (reseller recoding) stated explicitly |
| Gate + blockers completeness | 1.0 | `match_confiavel` + Cobertura + Bloqueadores all present and consistent |
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
| conditions | Internal prototype used only while the live reverse-image engine is still unbuilt, never shipped to production |
| approver | Author self-certification with comment explaining prototype-only scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d -- prototypes must be promoted to >= 7.0 or removed from repo |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H07 (a reordered section breaks StructuredResultView, which is frozen to fields\|table\|list) |

## Examples

# Examples: product-match-builder
## Golden Example
INPUT: "Create a product_match spec for the supplier-vs-MercadoLivre catalog matcher"
OUTPUT:
```yaml
id: p04_pm_visual_catalog_match
kind: product_match
pillar: P04
version: "1.0.0"
created: "2026-07-02"
updated: "2026-07-02"
author: "builder_agent"
name: "Supplier x Marketplace Visual Catalog Match"
contract_version: "1.0"
match_join_keys: [photo, dimension, supplier_code]
match_exclude_keys: [ean, gtin, barcode]
match_engine: none
match_confidence_floor: 0.7
audit_enabled: true
audit_min_photo_px: 200
quality: null
```
## Overview
Joins a supplier catalog item to a marketplace listing by a composite non-key
(photo+dimension+supplier_code); EAN/GTIN/barcode are structurally excluded because every
reseller recodes them. Runs the catalog-audit side-effect (text-vs-photo divergence, low-res
photo) on local item data regardless of network access. Consumed by the N03 dashboard run
(verb=analyze) and soft-imported by `sourcing_opportunity.py` (N06) for its own audit stage.
## Input Contract
| key | type | required | default |
|-----|------|:---:|---------|
| items | object[] | yes | -- |
| match_join_keys | string[] | no | [photo, dimension, supplier_code] |
| match_engine | enum | no | none |
| match_confidence_floor | number | no | 0.7 |
| audit_enabled | boolean | no | true |
| audit_min_photo_px | number | no | 200 |
| match_exclude_keys (internal) | string[] | no | [ean, gtin, barcode] |
## Output Sections
The frozen shape below mirrors `MOLD_PRODUCT_MATCH` (apps/dashboard_web/lib/molds.ts) -- its own
illustrative "dados simulados" reference rows. A REAL run today (match_engine=none, the default)
returns every match row as honest NAO at 0.0 confidence instead (product_match.py:386-393); the
audit section is the one that is genuinely live offline.
1. `Resultado do match` (table) -- cols [Codigo, Match?, Fonte casada, Confianca]
2. `Auditoria de catalogo` (list) -- cadastral/photo divergence flags
3. `Proveniencia` (fields) -- Motor de match, Chave de casamento, Fontes consultadas, Status por
   fonte, Honest-null offline
4. `Veredito` (fields) -- `match_confiavel`, Cobertura, Bloqueadores
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p04_pm_ pattern (H02 pass)
- kind: product_match (H04 pass)
- match_join_keys, match_engine, match_confidence_floor all present (H06 pass)
- 4 sections in `MOLD_PRODUCT_MATCH` order/layout (H07 pass)
- EAN/GTIN/barcode documented as excluded, not as a join key (H08 pass)
- match_engine=none is a valid closed-enum value (H09 pass)
- Veredito carries `match_confiavel` + Cobertura + Bloqueadores (H10 pass)
## Anti-Example
INPUT: "Create a product matcher"
BAD OUTPUT:
```yaml
id: product-matcher
kind: matcher
pillar: tools
name: Product Matcher
join_key: ean
capabilities: [match]
quality: 9.0
tags: [match]
```
Matches products by barcode using AI vision.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p11_qg_quality_gate | sibling | 0.44 |
| [[bld_schema_product_match]] | upstream | 0.40 |
| p08_adr_opportunity_matrix_kind | upstream | 0.38 |
