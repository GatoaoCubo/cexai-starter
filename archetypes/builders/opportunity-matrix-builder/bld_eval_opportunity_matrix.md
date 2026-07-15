---
kind: quality_gate
id: p11_qg_opportunity_matrix
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for opportunity_matrix
quality: null
title: "Quality Gate Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, quality_gate]
tldr: "Quality gate with HARD and SOFT scoring for opportunity_matrix"
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F7_govern"
keywords: [opportunity_matrix construction, quality gate opportunity matrix, opportunity_matrix, builder, quality_gate, sourcing_confiavel, honest-null, golden example, anti-example, hard gates]
density_score: 0.85
related:
  - bld_instruction_opportunity_matrix
  - opportunity-matrix-builder
  - p10_mem_opportunity_matrix_builder
  - bld_knowledge_card_opportunity_matrix
  - p08_adr_opportunity_matrix_kind
---
## Quality Gate

## Definition
| metric | threshold | operator | scope |
|--------|-----------|----------|-------|
| Section shape fidelity | 8/8 | == | vs MOLD_SOURCING_OPPORTUNITY |
| Table cell drift | 0 | == | every table row vs its columns length |

## HARD Gates
| ID | Check | Fail Condition |
|----|-------|-----------------|
| H01 | YAML frontmatter valid | Missing or invalid frontmatter |
| H02 | ID matches pattern | ID does not match ^p11_om_[a-z][a-z0-9_]+$ |
| H03 | kind field matches 'opportunity_matrix' | kind field invalid |
| H04 | All 8 sections present, frozen order | Missing/reordered/renamed section vs MOLD_SOURCING_OPPORTUNITY |
| H05 | Table columns match frozen sets | Matriz (9 cols) / Leitura (5) / Verificacao (5) / Match (4) mismatch |
| H06 | Named gate present | Section 8 missing `sourcing_confiavel` + its conditions |
| H07 | No fabricated market data | A sell price/demand level shown as real when source is offline/blocked (must be honest-null) |
| H08 | EAN/GTIN/barcode excluded from join | Any join-key reference to ean/gtin/barcode |

## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| D01 | Section fidelity | 0.20 | 8/8 byte-identical = 1.0, 1 drift = 0.6 |
| D02 | Provenance completeness | 0.15 | Fontes consultadas + sem dado + status + banda = 1.0, partial = 0.6 |
| D03 | Gate clarity | 0.15 | Conditions spelled out + evaluated = 1.0, gate value only = 0.4 |
| D04 | Honest-null discipline | 0.15 | Zero fabricated cells = 1.0, 1+ fabricated = 0.0 (also fails H07) |
| D05 | Cobertura transparency | 0.10 | Manual bucket + cauda-longa counted, not dropped = 1.0 |
| D06 | Margin math traceability | 0.10 | Fee/freight model + BRUTA/LIQUIDA labeled = 1.0 |
| D07 | Documentation | 0.10 | Full = 1.0, partial = 0.7 |
| D08 | Versioning | 0.05 | Versioned = 1.0, unversioned = 0.5 |

## Actions
| Score | Action |
|-------|--------|
| GOLDEN | Approve |
| PUBLISH | Publish |
| REVIEW | Peer review |
| REJECT | Reject |

## Bypass
| conditions | approver | audit trail |
|-----------|----------|-------------|
| Founder-approved tenant deploy despite an offline scaffold (no live demand credential) | N06 lead | "Bypassed by N06 lead on <date> -- offline scaffold accepted for structural review" |

## Examples

## Golden Example (excerpt -- offline scaffold, honest)
```markdown
## Veredito + proximos passos
| Campo | Valor |
|-------|-------|
| sourcing_confiavel | false |
| Condicoes do gate | margem_bruta_top >= 25% AND top-N verificado AND nenhum item critico sem preco AND frescor != RED |
| Avaliacao das condicoes | BLOQUEADO: offline -- demanda blocked: offline, sem preco de mercado para avaliar margem |
| Acoes ranqueadas | 1) Executar com credencial + demand_sources; 2) verificar top-10 (preco web = teto); 3) recodificar os itens do bucket "manual / sem preco" |
| Proximo passo encadeavel | N/A (gate BLOQUEADO) |
```
Why it passes: names the gate, spells out all 4 conditions, evaluates them honestly against the offline state, and never invents a market price.

## Anti-Example 1: Fabricated Market Price
```markdown
| # | Produto | Fornecedor (desc%) | Custo | Preco mercado | Margem | Demanda | Relevancia | Score |
|---|---------|--------------------|-------|--------------|--------|---------|------------|------|
| 1 | Furadeira 650W | FerragensBR (32%) | R$ 142,80 | R$ 299,90 | 52% | ALTA | ALTA | 0.91 |
```
## Why it fails
The row shows a real-looking market price and demand level with no `credential`/`demand_sources` declared and no matching Proveniencia entry -- H07 fails: a plausible invented value where the generator's offline path requires `"nao pesquisado"` (S5 honest-null).

## Anti-Example 2: Missing Gate Conditions
```markdown
## Veredito + proximos passos
sourcing_confiavel: true
```
## Why it fails
States the gate value with no boolean conditions and no evaluation line -- fails H06 (S4 requires the conditions spelled out, not just the verdict) and gives a downstream capability nothing to chain on.

### H_RELATED: Cross-Reference Check (HARD)
- [ ] `related:` frontmatter field populated (min 3 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream or sibling reference
- Gate: REJECT if < 3 entries (auto-populated by cex_wikilink.py at F6.5)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_opportunity_matrix]] | related | 0.45 |
| [[opportunity-matrix-builder]] | related | 0.42 |
| [[p10_mem_opportunity_matrix_builder]] | related | 0.38 |
| [[bld_knowledge_opportunity_matrix]] | related | 0.35 |
| p08_adr_opportunity_matrix_kind | upstream | 0.33 |
